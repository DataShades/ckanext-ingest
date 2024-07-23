# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## Unreleased

<small>[Compare with latest](https://github.com/DataShades/ckanext-ingest/compare/v1.4.2...HEAD)</small>

### Bug Fixes

- fix reporting on example view page ([1be4ce5](https://github.com/DataShades/ckanext-ingest/commit/1be4ce54120f3c01237a15dc37f0a83119d260ae) by Sergey Motornyuk).

<!-- insertion marker -->
## [v1.4.2](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.4.2) - 2024-07-23

<small>[Compare with v1.4.1](https://github.com/DataShades/ckanext-ingest/compare/v1.4.1...v1.4.2)</small>

### Bug Fixes

- include config declarations into package ([4f1f016](https://github.com/DataShades/ckanext-ingest/commit/4f1f01613861e5b8085de9c5a1e8ddf0a576449e) by Sergey Motornyuk).

## [v1.4.1](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.4.1) - 2024-04-02

<small>[Compare with v1.4.0](https://github.com/DataShades/ckanext-ingest/compare/v1.4.0...v1.4.1)</small>

### Features

- add ingest_options.default` ([638e4e0](https://github.com/DataShades/ckanext-ingest/commit/638e4e063d3dd4abcc9d342f127a78c2413fed09) by Sergey Motornyuk).
- with_extras shared function ([1ed8976](https://github.com/DataShades/ckanext-ingest/commit/1ed8976cbc4febb0061aaca417b23b9ecec9e92a) by Sergey Motornyuk).
- Record.get_extra method ([473aa1a](https://github.com/DataShades/ckanext-ingest/commit/473aa1a7b10f68d7118563342011528635ca9550) by Sergey Motornyuk).
- add get_extra and get_record_options to shared` ([a46a573](https://github.com/DataShades/ckanext-ingest/commit/a46a573855840643fbecdcdff8011ec3ee747670) by Sergey Motornyuk).

## [v1.4.0](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.4.0) - 2023-09-26

<small>[Compare with v1.3.0](https://github.com/DataShades/ckanext-ingest/compare/v1.3.0...v1.4.0)</small>

### Features

- enable xlsx strategy ([ba8ec2e](https://github.com/DataShades/ckanext-ingest/commit/ba8ec2e85574adaf7d88dedf851a9c829da9b15d) by Sergey Motornyuk).
- ParsingStrategy renamed to ExtractionStrategy ([58e831a](https://github.com/DataShades/ckanext-ingest/commit/58e831a9580ec6dbdd1aad17cc42baa1eecd0f85) by Sergey Motornyuk).
- Update csv strategy ([e882806](https://github.com/DataShades/ckanext-ingest/commit/e8828067550ed905ee1ff197d12f4f71ce3e13c2) by Sergey Motornyuk).
- Rename transformation option `alias` into `aliases` ([e617a50](https://github.com/DataShades/ckanext-ingest/commit/e617a50e480612df46eaac17b9840f4d5f3996c4) by Sergey Motornyuk).
- Record.ingest regurns shared.IngestionResult ([8eb7468](https://github.com/DataShades/ckanext-ingest/commit/8eb7468a9c3d530b56126a561ecd3383ec147747) by Sergey Motornyuk).
- TypedRecord base class removed ([49dde31](https://github.com/DataShades/ckanext-ingest/commit/49dde31902bb0dddf6584e21ae2a49d1c6e846bc) by Sergey Motornyuk).
- `update_existing` moded into `options["resource_options"]["update_existing"] ([357fe04](https://github.com/DataShades/ckanext-ingest/commit/357fe040cb292079748137f27298e90e49cc2a0a) by Sergey Motornyuk).
- API parameter `extras` renamed to `options`. ([26738e5](https://github.com/DataShades/ckanext-ingest/commit/26738e5a5d5ee9681f18e1ebb18a4ef49f3b8b0b) by Sergey Motornyuk).
- API actions accept `strategy` parameter. Auto-detection using mimetype used when `strategy` is missing ([cce4078](https://github.com/DataShades/ckanext-ingest/commit/cce40780e4494ddf82584c6ac6a02355dc4be8d6) by Sergey Motornyuk).
- Record.set_options removed ([52de560](https://github.com/DataShades/ckanext-ingest/commit/52de560f8f4e79759a941efa16abffa5160756af) by Sergey Motornyuk).
- start/rows parameters of API actions renamed to skip/take ([f8240de](https://github.com/DataShades/ckanext-ingest/commit/f8240dec5ee812fcd0aec52dd6da26772ef277dc) by Sergey Motornyuk).
- IIngest.get_ingest_strategies returns dict[str,ParsingStrategy] ([2f9da5b](https://github.com/DataShades/ckanext-ingest/commit/2f9da5b716be5bfdb2cfddd5a48fb31f9598b31a) by Sergey Motornyuk).
- remove `process` command ([773d27b](https://github.com/DataShades/ckanext-ingest/commit/773d27ba0acdbb465b4467de5532bac47d610643) by Sergey Motornyuk).
- add config declarations ([bd0b81a](https://github.com/DataShades/ckanext-ingest/commit/bd0b81aeabed791e163b5ec0a87c636391c38112) by Sergey Motornyuk).
- min CKAN v2.10 requirement ([bd07a13](https://github.com/DataShades/ckanext-ingest/commit/bd07a13b37197c56ee16d37abe038030a78dc04b) by Sergey Motornyuk).

## [v1.3.0](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.3.0) - 2023-03-25

<small>[Compare with v1.2.6](https://github.com/DataShades/ckanext-ingest/compare/v1.2.6...v1.3.0)</small>

### Features

- PackageRecord and ResourceRecord has a profile attribute ([702003e](https://github.com/DataShades/ckanext-ingest/commit/702003e2201c1c80f72fb55fb6da47632d3fafee) by Sergey Motornyuk).
- transform_* accepts options profile ([01acffc](https://github.com/DataShades/ckanext-ingest/commit/01acffc546abf51effad75e77bbd1db3d237996a) by Sergey Motornyuk).

## [v1.2.6](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.2.6) - 2022-11-04

<small>[Compare with v1.2.5](https://github.com/DataShades/ckanext-ingest/compare/v1.2.5...v1.2.6)</small>

### Bug Fixes

- allow transferring resource ownership ([68d5eed](https://github.com/DataShades/ckanext-ingest/commit/68d5eed877981ade78f3e72dcf58ce1e7b0f37ea) by Sergey Motornyuk).

## [v1.2.5](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.2.5) - 2022-04-07

<small>[Compare with v1.2.4](https://github.com/DataShades/ckanext-ingest/compare/v1.2.4...v1.2.5)</small>

## [v1.2.4](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.2.4) - 2022-04-04

<small>[Compare with v1.2.3](https://github.com/DataShades/ckanext-ingest/compare/v1.2.3...v1.2.4)</small>

## [v1.2.3](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.2.3) - 2022-02-23

<small>[Compare with v1.2.2](https://github.com/DataShades/ckanext-ingest/compare/v1.2.2...v1.2.3)</small>

## [v1.2.2](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.2.2) - 2022-02-23

<small>[Compare with v1.2.0](https://github.com/DataShades/ckanext-ingest/compare/v1.2.0...v1.2.2)</small>

## [v1.2.0](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.2.0) - 2022-02-22

<small>[Compare with v1.0.0](https://github.com/DataShades/ckanext-ingest/compare/v1.0.0...v1.2.0)</small>

## [v1.0.0](https://github.com/DataShades/ckanext-ingest/releases/tag/v1.0.0) - 2022-02-07

<small>[Compare with first commit](https://github.com/DataShades/ckanext-ingest/compare/5218fb4ae2e6c806e027ff44a5a17bd41377967c...v1.0.0)</small>

