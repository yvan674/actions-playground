# actions-playground

[![Endpoint](https://github.com/yvan674/actions-playground/actions/workflows/endpoint.yml/badge.svg)](https://github.com/yvan674/actions-playground/actions/workflows/endpoint.yml)
[![Receiver](https://github.com/yvan674/actions-playground/actions/workflows/receiver.yml/badge.svg)](https://github.com/yvan674/actions-playground/actions/workflows/receiver.yml)
[![Frontend](https://github.com/yvan674/actions-playground/actions/workflows/frontend.yml/badge.svg)](https://github.com/yvan674/actions-playground/actions/workflows/frontend.yml)
[![RabbitMQ](https://github.com/yvan674/actions-playground/actions/workflows/rabbitmq.yml/badge.svg)](https://github.com/yvan674/actions-playground/actions/workflows/rabbitmq.yml)


Monorepo structured repo to play around and test github actions.

## Why?

Man, GitHub Actions are hard, especially multi-step workflows.
If you think they aren't hats off to you but for everyone else, I think it's fair to say that CI/CD is hard to set up in the first place.

We don't want to actually mess up the main repo with all of this mess, so I made a new repo just to test out how this works.
I'm happy to say, it does now!

## GitHub Workflow Environments Experiments

This repo includes an experiment for environment-aware validation in GitHub Actions.

### What is configured

- A reusable workflow that validates configuration for a target environment.
- A pull request workflow that calls the reusable workflow with the `staging` environment.
- A release workflow that calls the reusable workflow with the `prod` environment.
- Two local composite actions used by the reusable workflow:
	- `run-tests`: fails if required variables/secrets are missing.
	- `log-vars`: prints variables and the active GitHub environment name.

### Required values

The reusable workflow expects these names to exist as GitHub Actions variables/secrets:

| Name | Type |
| --- | --- |
| SERVICE_NAME | Variable |
| ENVIRONMENT | Variable |
| API_URL | Variable |
| PROJECT_ID | Variable |
| API_KEY | Secret |
| WORKLOAD_IDENTITY_PROVIDER | Secret |

You can define these at repository scope, environment scope (`staging` / `prod`), or a mix of both.
Environment-scoped values override repository-scoped values when the job runs in that environment.

### Workflow mapping

- Pull request workflow uses `staging`.
- Release workflow (tag pattern `release-*`) uses `prod`.

Both workflows invoke the same reusable workflow and inherit secrets from the caller.
