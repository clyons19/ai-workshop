# AI Workshop

(WIP) A series of Python, Jupyter Notebook, and informational markdown files to walk through the basics of Python, Pandas, and Deep Learning with TensorFlow. Deep Learning with PyTorch to be added at a future date.

### Getting Started

1. [Download Python](https://www.python.org/downloads)
	* [Windows Releases](https://www.python.org/downloads/windows/): If running on Windows, Python
	  3.7 -- 3.10 must be install in order to use TensorFlow as TensorFlow stopped supporting
	  Windows after tensorflow-2.10.0
1. Within a terminal window
	1. Create a new _venv_ for this project by running `py -m venv ai-workshop`
		* Use `py -<version>` in place of `py` below to use a specific version of python
	1. Activate the virtual environment by running `ai-workshop\Scripts\activate`
	1. Install the requirements for this project by running one of the following:
		* All modules support (requires python 3.7--3.10): `pip install -r "<path-to-project>\requirements.txt"`
		* TensorFlow, Pandas, and Python modules support (requires python 3.7--3.10): `pip install -r "<path-to-project>\requirements-tf.txt"`
		* PyTorch, Pandas, and Python modules support: TBD
		* Pandas and Python modules support: `pip install -r "<path-to-project>\requirements-pd.txt"`
1. Run the file _0-check_env.py_ within the *ai-workshop* environment to validate package installation
	* TensorFlow and PyTorch packages may fail to validate depending on which requirements you
	  from above. That is OK

## [Python Tutorial](python-tutorial)

The Python tutorial files are based, in part, upon the following GitHub repository(ies):
1. [Akuli Python 3 Tutorial](https://github.com/Akuli/python-tutorial)

## [Pandas Tutorial](pandas-tutorial)

The Pandas Tutorial files are based, in part, upon the following GitHub repository(ies):
1. [Stefmolin Pandas Workshop](https://github.com/stefmolin/pandas-workshop)

This tutorial contains notebooks for learning about Pandas. Read through and run the cells in each notebook to gain familiarity in working with Pandas. Please modify or add new cells of code to explore the introduced ideas more and strengthen your understanding. Each lesson contains exercises found in the [workbook notebook](pandas-tutorial\workbook.ipynb). Please attempt the exercises before looking at the solutions in the [workbook-solutions notebook](pandas-tutorial\workbook-solutions.ipynb).

| Lesson               | Notebook                                               |
| ---                  | ---                                                    |
| 1: Pandas Beginnings | [1-pandas-beginnings.ipynb](1-pandas-beginnings.ipynb) |

### Additional Resources

Here is a list of additional resources for Python, Pandas, and AI.

#### Python
1. [Official Python 3 Documentation Tutorial](https://docs.python.org/3/tutorial/index.html)
1. [Think Python - Allen Downey](https://greenteapress.com/thinkpython2/thinkpython2.pdf)

#### Pandas

#### AI