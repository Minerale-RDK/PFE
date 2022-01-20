docker image build -t client_captor docker-client-minimal_captor/v0.0.1/
docker image build -t serveur-generateur docker-server-minimal_generateur/v0.1.0/
docker run -d serveur-generateur
docker run client_captor 
