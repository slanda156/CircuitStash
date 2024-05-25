# Circuit Stash
> An Open Source part storage manager

I wanted a free storage manager for my electronics parts, that stores all information localy.
This is curently a python program runing and saving localy in a sqlite file.
You can create a part with an image and crate a location to store diffrent parts.


## Installation

Windows:
    Download the latest release and start the .exe

## Development setup

Download the repository of the desired version.
Make sure to have python 3.12 installed.

I recomend using an virual enviroment.

Go to the folder and install the dependencies.

```sh
python -m virtualenv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

If you want to run tests
```sh
pip install pytest
python -m pytest
```

If you want to generate the docs
```sh
pip install mkdocs mkdocs-material
python -m mkdocs build
```

## ToDo

* Add the possibility to use none local database
* Add multiple currencies

## Release History

* 0.0.1
    * Work in progress

## Meta

Christoph Heil – slandalp@gmail.com

Distributed under the MIT license. See [``License``](LICENSE) for more information.

[https://github.com/slanda156/CircuitStash](https://github.com/slanda156/CircuitStash)

I used this [https://github.com/dbader/readme-template](https://github.com/dbader/readme-template) as a template for the README

## Contributing

Till the first release its not possible to contribute
