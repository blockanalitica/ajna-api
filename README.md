# AJNA API

[![License: AGPL](https://img.shields.io/badge/License-AGPL-yellow.svg)](https://opensource.org/licenses/AGPL)


## Table of Contents

- [Introduction](#introduction)
- [Installation](#installation)
- [Testing](#testing)
- [Contribution guidelines](#contribution-guidelines)
- [License](#license)

## Introduction

### What is the Ajna Protocol?
The Ajna protocol is a noncustodial, peer-to-peer, permissionless lending, borrowing and trading system implemented for the Ethereum Virtual Machine that requires no governance or external price feeds to function.

### What is Ajna API?

Ajna API is Django-based web application that provides a RESTful API for the Ajna Analytics Dashboard. Built on top of Django and Django Rest Framework

The application is designed to interact seamlessly with various data sources, primarily utilizing Subgraph as the primary data source. This ensures that the API is always up-to-date with the latest information, providing accurate and reliable data for the Ajna Analytics Dashboard.

Ajna API serves as the backend for the Ajna Analytics Dashboard, which is a separate project with its own repository, focusing on the user interface and user experience. You can find the Ajna Analytics Dashboard UI project at this link: [Ajna Analytics Dashboard UI](https://github.com/blockanalitica/ajna-info)

## Installation

### Installation using Docker Compose

To install and run Ajna API using Docker Compose, follow these steps:

1. Clone the repository: `git clone https://github.com/blockanalitica/ajna-info-api.git`
2. Navigate to the project directory: `cd ajna-info-api`
3. Create a `.env` file with the necessary environment variables (see `.env.example` for an example)
4. Install dependencies: `docker compose build`
5. Run migrations: `docker compose run --rm web django-admin migrate`
6. Run `docker compose up` to start the application
7. Navigate to [http://localhost:8000/](http://localhost:8000/) to access the application

### Installation using `python manage.py`

To install and run Ajna API using `python manage.py`, follow these steps:

1. Clone the repository: `git clone https://github.com/blockanalitica/ajna-info-api.git`
2. Navigate to the project directory: `cd ajna-info-api`
3. Install dependencies: `pip install -r requirements.txt -r lint-requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Run the development server: `python manage.py runserver`
6. Navigate to [http://localhost:8000/](http://localhost:8000/) to access the application

## Testing

Ajna API uses [pytest](https://pytest.org/) for testing. To run the test suite, follow these steps:

1. Navigate to the project root directory.
2. Run the test suite: `pytest` or `docker compose run --rm web pytest` if using docker-compose

The test suite includes both unit tests and integration tests, and is designed to ensure that the API is functioning correctly and securely.

If you encounter any issues while running the test suite, please open an issue in the project repository.




## Contribution guidelines

If you'd like to contribute to Ajna API, please follow these guidelines:

1. Fork the repository and clone your fork locally.
2. Create a new branch for your feature or bug fix: `git checkout -b my-feature-branch`
3. Make your changes and commit them with a descriptive commit message.
4. Push your changes to your fork: `git push origin my-feature-branch`
5. Create a pull request against the main repository's `main` branch.
6. Wait for feedback or approval on your pull request. Be prepared to make changes if requested.
7. Once your pull request is merged, your changes will be included in the next release.

To ensure that your changes are accepted quickly, please follow these best practices:

- Write clear, concise commit messages that describe the changes you've made.
- Make sure your code is well-formatted and follows the project's existing style.
- Write tests for any new functionality or changes to existing functionality.
- Ensure that all tests pass before submitting a pull request.
- Be open to feedback and willing to make changes if requested.

We believe in maintaining a welcoming, inclusive, and harassment-free community for all contributors and users. To that end, we have adopted the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Please review the code of conduct before contributing to Ajna API.

Thank you for contributing to Ajna API!

### Code Style

Ajna API follows the code style guidelines set by the [Black](https://black.readthedocs.io/en/stable/), [isort](https://pycqa.github.io/isort/), and [Flake8](https://flake8.pycqa.org/en/latest/) code formatters and linter. Before submitting a pull request, please ensure that your code is formatted and linted using these tools.

You can install them using pip:

```sh
pip install -r lint-requiremets.txt
```

To format your code using Black and isort, navigate to the project directory and run:

```sh
black .
isort .
```

This will format and sort all Python files in the project directory and its subdirectories. If you encounter any issues with Black or isort, please refer to the [official documentation](https://black.readthedocs.io/en/stable/) and [isort documentation](https://pycqa.github.io/isort/).

To lint your code using Flake8, navigate to the project directory and run:

```sh
flake8 .
```

This will check all Python files in the project directory and its subdirectories for any syntax errors or style violations. If you encounter any issues with Flake8, please refer to the [official documentation](https://flake8.pycqa.org/en/latest/).

To format the code, you can either run each command individually as described in the previous section, or you can navigate to the project directory and run:

```sh
black . && isort . && flake8 .
```

This command will run all of the above commands in sequence and format your code according to the project's style guide.

#### Using Pre-Commit for Code Quality Checks

We use `pre-commit` to enforce code quality checks before commits are made to our repository. `pre-commit` is a tool that manages Git hooks, which are scripts that run automatically at certain points in the Git workflow. It provides a range of pre-built hooks, such as code formatters, linters, and security scanners, that can be easily integrated into a development workflow.

To manually run `pre-commit`, simply run the following command in your terminal:

```sh
pre-commit run --all-files
```

This will run all configured hooks on all files in your repository.

You can also run individual hooks or specify specific files to check. For more information on using `pre-commit`, see the [official documentation](https://pre-commit.com/).

##### Activate pre-commit

Install the hooks by running the following command in the root directory of your project:

```sh
pre-commit install
```

This will create a Git hook that runs every time you commit changes to your code.

Commit your changes and let the hooks do their work. If any issues are detected, the commit will be aborted and the issues will be displayed in the console. You can then fix the issues and try the commit again.

### Conventional Commits

At Ajna API, we use [Conventional Commits](https://www.conventionalcommits.org/) to format our commit messages in a consistent and standardized way. By following this convention, we can more easily understand the purpose and impact of each commit, and generate accurate release notes and changelogs.

Here are the basic rules for creating a Conventional Commit:

<type>[optional scope]: <description>

The <type> field must be one of the following:

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Changes that do not affect the meaning of the code (e.g. formatting)
- `refactor`: Changes to code that neither fix a bug nor add a feature
- `perf`: Changes that improve performance
- `test`: Adding or updating tests
- `build`: Changes to the build process or tools
- `ci`: Changes to the CI/CD pipeline
- `chore`: Other changes that don't modify src or test files

By using Conventional Commits, we can maintain a clear and organized commit history, which makes it easier for us to track changes and collaborate effectively as a team.


### Versioning with Release-Please

We use the [Release Please](https://github.com/googleapis/release-please) tool to manage versioning for our Docker images. This tool automatically creates a new Docker image and updates the version number in our `VERSION` file when a release is tagged in GitHub.

To use Release Please, you should follow these steps:

1. Create a new release in GitHub with a semantic version number (e.g. `v1.2.3`).
2. Release Please will automatically create a new branch with the same name as the release (e.g. `release-v1.2.3`), make any necessary changes to the `VERSION` file, and create a new commit.
3. Release Please will then create a pull request against the main branch that includes the new version number and any other relevant changes.
4. Review the pull request and merge it into the main branch to complete the release.

By using Release Please, we can ensure that our Docker images are versioned consistently and accurately, and that our `VERSION` file always reflects the current version of the image.

## License

This project is licensed under the AGPL License - see the [LICENSE](LICENSE) file for details.
