FROM tiangolo/uvicorn-gunicorn:python3.10-2023-03-27
SHELL ["/bin/bash", "-c"]
# now let's install the fucking MSSQL drivers
# https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server?view=sql-server-ver15#17
# cat /etc/issue.net tells you this image is based off Debian GNU/Linux 11
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update
# download oracle driver
WORKDIR /opt/oracle
RUN curl -O https://download.oracle.com/otn_software/linux/instantclient/2112000/instantclient-basic-linux.x64-21.12.0.0.0dbru.zip
RUN unzip instantclient-basic-linux.x64-21.12.0.0.0dbru.zip
RUN echo /opt/oracle/instantclient_21_12 > /etc/ld.so.conf.d/oracle-instantclient.conf
RUN ldconfig
# some random driver issues
RUN chmod +rwx /etc/ssl/openssl.cnf
RUN sed -i 's/TLSv1.2/TLSv1/g' /etc/ssl/openssl.cnf
RUN sed -i 's/SECLEVEL=2/SECLEVEL=1/g' /etc/ssl/openssl.cnf

# throw in build-essential to save us some time down the line
# libaio is for oracle driver: https://docs.oracle.com/en/database/oracle/oracle-database/21/lacli/install-instant-client-using-zip.html#GUID-D3DCB4FB-D3CA-4C25-BE48-3A1FB5A22E84
RUN ACCEPT_EULA=Y apt-get -y install build-essential msodbcsql18 mssql-tools18 mssql-tools unixodbc-dev libaio1
RUN echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN source ~/.bashrc
# now the real man fast api settings
ENV MAX_WORKERS=8
# now our app itself
WORKDIR /app
COPY . .

# pywin32 appears to be a dependency of azure-identity, but it is not needed on linux
RUN sed -i '/^pywin32==308/d' requirements.txt

# install
RUN python -m pip install -U pip
RUN pip install -r requirements.txt