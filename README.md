# Animal-AI Configuration Assistant

This library allows users to debug and visualise Animal-AI configuration files.

## Getting started
This section will guide you through installing and using Animal-AI Configuration Assistant locally.

### Prerequisites
- Python 3 - [Download Python 3](https://www.python.org/downloads/) (any version in the 3.9.x line)

### Installation
1. Clone this repository to your local machine
    ```sh
   git clone git@github.com:mgm21/aai-config-assist.git
   cd aai-config-assist
   ```
2. Set up your virtual environment in the root of the cloned repository
   1. Linux/macOS 
      ```sh
      python -m venv venv
      source venv/bin/activate
      ```
   2. Windows
      ```sh
      python -m venv venv
      venv\Scripts\activate
      ```

4. Install the required packages in the development environment
    ```shell
    pip install -r requirements.txt
    ```

### Using the library
1. Open the [checking_and_visualising.py](scripts/checking_and_visualising.py) file in an editor of your choice
(Vim, TextEdit, VS Code, Pycharm...)
2. Replace the `config_path` variable with the path from the repository root to your `.yaml` configuration file. For
example, if your configuration file is `aai-config-assist/config.yaml` then your path would be 
`os.path.join("example_configs", "config.yaml")`
3. Open Terminal, and navigate to the root of this repository. You can run `pwd` in Terminal to ensure that your
working directory is the `aai-config-assistant` repository on your local machine.
4. In Terminal, enter the following command to execute the [checking_and_visualising.py](scripts/checking_and_visualising.py)
   ```shell
   python -m scripts.checking_and_visualising
   ```
You should now see a visualisation of your configuration arena as well as a summary of the overlaps
between items in your configuration (in the Terminal log output).

If you run into any issues, please get in touch (see Contact section below).

## License
[MIT License](LICENSE)

## Contact
Matteo G. Mecattaf - [LinkedIn](https://www.linkedin.com/in/matteo-mecattaf/)