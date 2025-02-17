# Notes about installation

1. Activate venv
2. python -m pip install --upgrade pip
3. python -m pip install pip-tools pip_system_certs
4. pip-compile --resolver=backtracking requirements.in
5. pip-compile --resolver=backtracking --upgrade requirements.in
6. pip-compile --upgrade --upgrade-package 'requests<3.0' requirements.in
7. pip-compile --resolver=backtracking --upgrade dev-requirements.in
8. pip-sync requirements.txt dev-requirements.txt
