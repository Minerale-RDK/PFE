import subprocess

while True:
    subprocess.run("docker cp client1-captor:/test.csv test.csv")