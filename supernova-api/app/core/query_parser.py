from fastapi import Depends, Request
from multidict import MultiDict


class QueryParser(object):
    def __init__(self, param_config):
        self.param_config = param_config
        if "alias" in param_config:
            self.alias = param_config["alias"] + "."
            self.prefix = param_config["alias"]
        else:
            self.alias = ""
            self.prefix = ""

    @staticmethod
    def collect_query_param(request: Request):
        multi_dict = MultiDict(request.query_params.multi_items())
        new_dict = {}
        for k in set(multi_dict.keys()):
            k_values = multi_dict.getall(k)
            if len(k_values) > 1:
                new_dict[k] = k_values
            else:
                new_dict[k] = k_values[0]
        return new_dict

    def parse_query(self, request: Request, param_dict):
        if request is not None:
            param_dict = self.collect_query_param(request)
        sql_query = ""
        sql_params = {}
        # do the discrete params
        if "discrete" in self.param_config:
            for p in self.param_config["discrete"]:
                if p in param_dict:
                    v = param_dict[p]
                    if isinstance(v, list):
                        sql_query += (
                            f" and {self.alias}{p} in ("
                            + ", ".join(
                                [
                                    f":{self.prefix}{p}{i}"
                                    for i in range(len(v))
                                ]
                            )
                            + ")"
                        )
                        sql_params = {
                            **sql_params,
                            **{
                                f"{self.prefix}{p}{i}": n
                                for i, n in enumerate(v)
                            },
                        }
                    elif v is None:
                        sql_query += f" and {self.alias}{p} is null"
                    else:
                        sql_query += (
                            f" and {self.alias}{p} = :{self.prefix}{p}"
                        )
                        sql_params = {
                            **sql_params,
                            f"{self.prefix}{p}": param_dict[p],
                        }
        if "continuous" in self.param_config:
            for p in self.param_config["continuous"]:
                if p in param_dict:
                    v = param_dict[p]
                    if isinstance(v, list):
                        if v[0] is not None:
                            sql_query += f" and {self.alias}{p} >= :{self.prefix}{p}Start"
                            sql_params = {
                                **sql_params,
                                f"{self.prefix}{p}Start": v[0],
                            }
                        if v[1] is not None:
                            sql_query += (
                                f" and {self.alias}{p} < :{self.prefix}{p}End"
                            )
                            sql_params = {
                                **sql_params,
                                f"{self.prefix}{p}End": v[1],
                            }
                    else:
                        sql_query += f" and {self.alias}{p} = :{p}"
                        sql_params = {
                            **sql_params,
                            f"{self.prefix}{p}": param_dict[p],
                        }
        if "wildcard_like" in self.param_config:
            for p in self.param_config["wildcard_like"]:
                if p in param_dict:
                    v = param_dict[p]
                    sql_query += (
                        f" and LOWER({self.alias}{p}) LIKE '%{v.lower()}%'"
                    )
                    sql_params = {**sql_params, f"{self.prefix}{p}": v}
        if "discrete_trim" in self.param_config:
            for p in self.param_config["discrete_trim"]:
                if p in param_dict:
                    v = param_dict[p]
                    if isinstance(v, list):
                        sql_query += (
                            f" and TRIM({self.alias}{p}) in ("
                            + ", ".join(
                                [
                                    f":{self.prefix}{p}{i}"
                                    for i in range(len(v))
                                ]
                            )
                            + ")"
                        )
                        sql_params = {
                            **sql_params,
                            **{
                                f"{self.prefix}{p}{i}": n
                                for i, n in enumerate(v)
                            },
                        }
                    elif v is None:
                        sql_query += f" and TRIM({self.alias}{p}) is null"
                    else:
                        sql_query += (
                            f" and TRIM({self.alias}{p}) = :{self.prefix}{p}"
                        )
                        sql_params = {
                            **sql_params,
                            f"{self.prefix}{p}": param_dict[p],
                        }

        return {"query": sql_query, "params": sql_params}

    def __call__(self, request: Request, param_dict=None):
        if request is not None or param_dict is not None:
            return self.parse_query(request, param_dict)


class ElasticsearchQueryParser(object):
    """
    Note from Gunther:
    This elasticsearch query parser is tailored to create queries against
    the New Account Setup Elasticsearch cluster.
    The query parser is built around how the fields in the document are
    tokenized.
    """

    def __init__(self, param_config):
        self.param_config = param_config

    @staticmethod
    def collect_query_param(request: Request):
        multi_dict = MultiDict(request.query_params.multi_items())
        new_dict = {}
        for k in set(multi_dict.keys()):
            k_values = multi_dict.getall(k)
            if len(k_values) > 1:
                new_dict[k] = k_values
            else:
                new_dict[k] = k_values[0]
        return new_dict

    def parse_query(self, request: Request, param_dict, search_mode):
        if request is not None:
            param_dict = self.collect_query_param(request)
        filter = []
        query_body = []
        if "keyword" in self.param_config:
            for p in self.param_config["keyword"]:
                if p in param_dict:
                    v = param_dict[p]
                    filter.append(
                        {"terms": {p: v if isinstance(v, list) else [v]}}
                    )
        if "text" in self.param_config:
            for p in self.param_config["text"]:
                if p in param_dict:
                    v = param_dict[p]
                    query_body.append({"match_phrase": {p: {"query": v}}})
        if "edge_ngram" in self.param_config:
            for p in self.param_config["edge_ngram"]:
                if p in param_dict:
                    v = param_dict[p]
                    # stupid double dipping of addressline1 and addressline2
                    if (
                        p == "AddressLine1"
                        and "AddressLine2" not in param_dict
                    ) or (
                        p == "AddressLine2"
                        and "AddressLine1" not in param_dict
                    ):
                        if "*" in v:
                            query_body.append(
                                {
                                    "bool": {
                                        "should": [
                                            {
                                                "wildcard": {
                                                    "AddressLine1": {
                                                        "value": v,
                                                        "case_insensitive": True,
                                                    }
                                                }
                                            },
                                            {
                                                "wildcard": {
                                                    "AddressLine2": {
                                                        "value": v,
                                                        "case_insensitive": True,
                                                    }
                                                }
                                            },
                                        ]
                                    }
                                }
                            )
                        else:
                            query_body.append(
                                {
                                    "bool": {
                                        "should": [
                                            {"term": {"AddressLine1": v}},
                                            {"term": {"AddressLine2": v}},
                                        ]
                                    }
                                }
                            )
                    else:
                        if "*" in v:
                            query_body.append(
                                {
                                    "wildcard": {
                                        p: {
                                            "value": v,
                                            "case_insensitive": True,
                                        }
                                    }
                                }
                            )
                        else:
                            query_body.append(
                                {"match": {p: {"query": v, "operator": "AND"}}}
                            )
        result = {"query": {"bool": {"filter": filter}}}
        if query_body:
            if search_mode == "must":
                result["query"]["bool"]["must"] = query_body
            elif search_mode == "should":
                result["query"]["bool"]["should"] = query_body
                result["query"]["bool"]["minimum_should_match"] = 1
        return result

    def __call__(self, request: Request, param_dict=None, search_mode=None):
        return self.parse_query(request, param_dict, search_mode)


class TableValueConstructor(object):
    def __init__(self, keys, items):
        self.keys = keys
        self.items = items
        self.length = len(items)

    def row_value_expression(self):
        values_string = ",".join(
            [
                "(" + ",".join([f":{k}{i}" for k in self.keys]) + ")"
                for i in range(self.length)
            ]
        )
        return values_string

    def row_value_parameter(self):
        parameter = {
            f"{k}{i}": s[k] if isinstance(s, dict) else getattr(s, k, None)
            for i, s in enumerate(self.items)
            for k in self.keys
        }
        return parameter
