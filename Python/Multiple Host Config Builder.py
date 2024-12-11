def read_file():
    # Reading the hostanames
    """ example of the csv file
    Hostname
    host1
    host2
    host3
    """
    while True:
        file = input("Enter the Host File name to read: ")
        try:
            with open(file, "r", newline="") as host_file:
                host_file.readline()  # Reading Header
                hostnames = host_file.readlines()
                hostnames = [line.rstrip("\r\n") for line in hostnames]  # Removing the \r\n
                return hostnames
        except FileNotFoundError:
            print(f"No such file or directory: {file}")


def config_gen(config, hostnames):
    # Building the configuration
    full_config = []
    for host in hostnames:
        full_config.append("#"*60 + "\n")
        full_config.append("{:!^60}".format(host) + "\n")
        full_config.append("#" * 60 + "\n")
        for line in config:
            full_config.append(line + "\n")
    return full_config


def write_file(file_name, config_file):
    # Writing the config to a file
    with open(file_name, "w") as write:
        write.write("Configuration\n")
        for line in config_file:
            write.write(line)
if __name__ == "__main__":
    configuration = [
        "config t",
        "<commands>",
        "end",
        "write",
        "!"]
    
    hosts = read_file()
    full_config = config_gen(configuration, hosts)
    write_file(str(input("What is the output file name: ")), output)
