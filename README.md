# PrivateKV

## SSH Setup with Podman

1. Generate an SSH keypair, press enter twice when prompted to omit password.

    ```
    ssh-keygen -m PEM -f pkv_test
    ```

2. Start the container

    ```
    podman run -e SSH_USERS=pkv:1000:1000 \
        -v $PWD/pkv_test.pub:/etc/authorized_keys/pkv:z \
        -P --name pkv_sftp -d panubo/sshd
    ```

3. Determine port number on the host.

    ```
    podman port -l
    ```
