# Changelog

## [v0.5.1](https://github.com/nedap/deidentify/tree/v0.5.1) (2020-09-04)

[Full Changelog](https://github.com/nedap/deidentify/compare/v0.5.0...v0.5.1)

**Merged pull requests:**

- Fix version and tag creation in release script [\#31](https://github.com/nedap/deidentify/pull/31) ([jantrienes](https://github.com/jantrienes))

## [v0.5.0](https://github.com/nedap/deidentify/tree/v0.5.0) (2020-09-04)

[Full Changelog](https://github.com/nedap/deidentify/compare/v0.4.0...v0.5.0)

**Merged pull requests:**

- Update dependencies in environment.yml [\#30](https://github.com/nedap/deidentify/pull/30) ([jantrienes](https://github.com/jantrienes))
- Remove upper bound on torch version [\#29](https://github.com/nedap/deidentify/pull/29) ([jantrienes](https://github.com/jantrienes))
- Fix whitespace token issue with newer flair versions [\#28](https://github.com/nedap/deidentify/pull/28) ([jantrienes](https://github.com/jantrienes))
- Fix call to run\_deduce with "ons" corpus [\#27](https://github.com/nedap/deidentify/pull/27) ([jantrienes](https://github.com/jantrienes))

## [v0.4.0](https://github.com/nedap/deidentify/tree/v0.4.0) (2020-09-04)

[Full Changelog](https://github.com/nedap/deidentify/compare/v0.3.3...v0.4.0)

**Merged pull requests:**

- Invalidate semaphore cache when conda env changed [\#26](https://github.com/nedap/deidentify/pull/26) ([jantrienes](https://github.com/jantrienes))
- Add dateinfer and nameparser to setup.py [\#25](https://github.com/nedap/deidentify/pull/25) ([jantrienes](https://github.com/jantrienes))
- Add surrogate generation demo to README [\#24](https://github.com/nedap/deidentify/pull/24) ([jantrienes](https://github.com/jantrienes))
- Add autopep8 and isort to dev requirements and remove pylint bound [\#23](https://github.com/nedap/deidentify/pull/23) ([jantrienes](https://github.com/jantrienes))
- Gracefully handle surrogate replacement for shuffle without choices [\#22](https://github.com/nedap/deidentify/pull/22) ([jantrienes](https://github.com/jantrienes))
- Add utility API to generate surrogates for a set of annotated documents [\#21](https://github.com/nedap/deidentify/pull/21) ([jantrienes](https://github.com/jantrienes))

## [v0.3.3](https://github.com/nedap/deidentify/tree/v0.3.3) (2020-08-07)

[Full Changelog](https://github.com/nedap/deidentify/compare/v0.3.2...v0.3.3)

**Closed issues:**

- Question about hardware required for model training [\#14](https://github.com/nedap/deidentify/issues/14)
- Semaphore 2 : missing auto\_cancel parameter in semaphore.yml [\#12](https://github.com/nedap/deidentify/issues/12)

**Merged pull requests:**

- Fix BiLSTM-CRF with consecutive whitespace tokens [\#20](https://github.com/nedap/deidentify/pull/20) ([jantrienes](https://github.com/jantrienes))
- Pin torch version in environment.yml [\#19](https://github.com/nedap/deidentify/pull/19) ([jantrienes](https://github.com/jantrienes))
- Add efficiency benchmark [\#18](https://github.com/nedap/deidentify/pull/18) ([jantrienes](https://github.com/jantrienes))
- Add requirements-dev.txt to list explicit dev requirements [\#17](https://github.com/nedap/deidentify/pull/17) ([jantrienes](https://github.com/jantrienes))
- Add example on available tags per tagger [\#16](https://github.com/nedap/deidentify/pull/16) ([jantrienes](https://github.com/jantrienes))
- Add brat annotation config [\#15](https://github.com/nedap/deidentify/pull/15) ([jantrienes](https://github.com/jantrienes))
- Add semaphore auto\_cancel for branches other than master [\#13](https://github.com/nedap/deidentify/pull/13) ([jantrienes](https://github.com/jantrienes))

## [v0.3.2](https://github.com/nedap/deidentify/tree/v0.3.2) (2020-01-16)

[Full Changelog](https://github.com/nedap/deidentify/compare/v0.3.1...v0.3.2)

**Merged pull requests:**

- Fix bug in setup.py [\#11](https://github.com/nedap/deidentify/pull/11) ([jantrienes](https://github.com/jantrienes))

## [v0.3.1](https://github.com/nedap/deidentify/tree/v0.3.1) (2020-01-16)

[Full Changelog](https://github.com/nedap/deidentify/compare/v0.3.0...v0.3.1)

**Merged pull requests:**

- Add bound on torch version [\#10](https://github.com/nedap/deidentify/pull/10) ([jantrienes](https://github.com/jantrienes))

## [v0.3.0](https://github.com/nedap/deidentify/tree/v0.3.0) (2020-01-16)

[Full Changelog](https://github.com/nedap/deidentify/compare/model_crf_ons_tuned-v0.1.0...v0.3.0)

**Merged pull requests:**

- Remove non-PyPI dependencies [\#9](https://github.com/nedap/deidentify/pull/9) ([jantrienes](https://github.com/jantrienes))
- Add utility function to mask sensitive PHI with placeholder [\#8](https://github.com/nedap/deidentify/pull/8) ([jantrienes](https://github.com/jantrienes))
- Add tagger parameter to configure pipeline verbosity [\#7](https://github.com/nedap/deidentify/pull/7) ([jantrienes](https://github.com/jantrienes))
- Update example text in README [\#6](https://github.com/nedap/deidentify/pull/6) ([jantrienes](https://github.com/jantrienes))
- Add a default cache path to store downloaded models [\#5](https://github.com/nedap/deidentify/pull/5) ([jantrienes](https://github.com/jantrienes))
- Add LICENSE [\#4](https://github.com/nedap/deidentify/pull/4) ([jantrienes](https://github.com/jantrienes))
- Clarify docs regarding experiment environment [\#3](https://github.com/nedap/deidentify/pull/3) ([jantrienes](https://github.com/jantrienes))
- Add documentation [\#2](https://github.com/nedap/deidentify/pull/2) ([jantrienes](https://github.com/jantrienes))
- Add model download script [\#1](https://github.com/nedap/deidentify/pull/1) ([jantrienes](https://github.com/jantrienes))



\* *This Changelog was automatically generated by [github_changelog_generator](https://github.com/github-changelog-generator/github-changelog-generator)*
