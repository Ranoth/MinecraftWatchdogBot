# Changelog

## [1.9.2](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.9.1...v1.9.2) (2026-02-24)


### Bug Fixes

* Increase rcon timeout time to 30 seconds for slow commands ([6073c70](https://github.com/Ranoth/MinecraftWatchdogBot/commit/6073c70aeffc48c8df85d237bc2f5bcf3a2874b4))

## [1.9.1](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.9.0...v1.9.1) (2026-02-24)


### Bug Fixes

* Timeout when bot takes more than 3 seconds to respond ([11d1fed](https://github.com/Ranoth/MinecraftWatchdogBot/commit/11d1fed5c49e5fb6884f1ae5f989b989bcefee1c))

## [1.9.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.8.0...v1.9.0) (2026-02-24)


### Features

* Add locate command ([7e196a2](https://github.com/Ranoth/MinecraftWatchdogBot/commit/7e196a21649a621fc2cd1c016ea232ed095676a6))
* Commands are now guild specific ([9e640b3](https://github.com/Ranoth/MinecraftWatchdogBot/commit/9e640b3ab242b88ea0a376d85f18a9e44248aea9))

## [1.8.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.7.1...v1.8.0) (2026-02-23)


### Features

* Add RCON command sending support for all configured containers ([3f7573f](https://github.com/Ranoth/MinecraftWatchdogBot/commit/3f7573f0ce17f2bded8445033ff55a1483ef79cd))

## [1.7.1](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.7.0...v1.7.1) (2025-12-08)


### Bug Fixes

* commands processed twice ([1f5083c](https://github.com/Ranoth/MinecraftWatchdogBot/commit/1f5083c67a118c144af87025ee5a011b8052845c))

## [1.7.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.6.1...v1.7.0) (2025-12-08)


### Features

* Bot able to send random photos of my cat ([cf63427](https://github.com/Ranoth/MinecraftWatchdogBot/commit/cf63427bcdfbb9f571e105dcb63c2a77764f950d))

## [1.6.1](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.6.0...v1.6.1) (2025-12-02)


### Bug Fixes

* Bot sends less new messages when servers restart ([61e4f17](https://github.com/Ranoth/MinecraftWatchdogBot/commit/61e4f17c1bb8e5c7acf3fa2379507d3c2d798d58))

## [1.6.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.5.0...v1.6.0) (2025-11-24)


### Features

* Add logging file rotation and compression ([086af97](https://github.com/Ranoth/MinecraftWatchdogBot/commit/086af97f13d1db79a3707d0ce38359ba251a393c))
* Add queue system for container startup updates ([2f7d1c0](https://github.com/Ranoth/MinecraftWatchdogBot/commit/2f7d1c0be19dff1f3cd8dfb95df874175144d3a7))

## [1.5.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.4.0...v1.5.0) (2025-11-23)


### Features

* Add status updates to startup ongoing message. ([19203ee](https://github.com/Ranoth/MinecraftWatchdogBot/commit/19203eee112c39a76b14db79986d047ddc7ff583))

## [1.4.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.3.2...v1.4.0) (2025-11-22)


### Features

* Add health check ([e7f39bb](https://github.com/Ranoth/MinecraftWatchdogBot/commit/e7f39bbb4a0c70ffa6e898f76d56def1843ed088))

## [1.3.2](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.3.1...v1.3.2) (2025-11-22)


### Bug Fixes

* Remove error trying to channel ([ff31377](https://github.com/Ranoth/MinecraftWatchdogBot/commit/ff31377a292fc17bc7e4706b38ebc0b558ca3e12))

## [1.3.1](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.3.0...v1.3.1) (2025-11-22)


### Bug Fixes

* Add missing space in death embed and fix chat message detection ([b47b700](https://github.com/Ranoth/MinecraftWatchdogBot/commit/b47b700cbe1bf6776cddeaedd51cc4d64bf45f11))

## [1.3.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.2.2...v1.3.0) (2025-11-22)


### Features

* Add ability to monitor logs for multiple minecraft servers at the same time. Need to fix commands ([d0147ac](https://github.com/Ranoth/MinecraftWatchdogBot/commit/d0147ac0874e977e1906de609a79dc0f5d6b8d51))

## [1.2.2](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.2.1...v1.2.2) (2025-11-21)


### Bug Fixes

* Error reading ghost log lines no longer hinder the bot's ability to read valid lines ([b7443e4](https://github.com/Ranoth/MinecraftWatchdogBot/commit/b7443e4d69dbc52225726f9d245c6ae6abda5b5c))

## [1.2.1](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.2.0...v1.2.1) (2025-11-16)


### Bug Fixes

* Java stacktrace multiline logs do no longer temporarily stop bot from monitoring logs. ([1048951](https://github.com/Ranoth/MinecraftWatchdogBot/commit/10489516c6fc8873ba4b8db5dcd8e95a51f93474))

## [1.2.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.1.2...v1.2.0) (2025-11-14)


### Features

* Add death tracking ([3cf36f0](https://github.com/Ranoth/MinecraftWatchdogBot/commit/3cf36f0e0e66129543ab4c8578734698e915bd00))

## [1.1.2](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.1.1...v1.1.2) (2025-11-10)


### Bug Fixes

* Monitoring not crashing anymore ([209b6db](https://github.com/Ranoth/MinecraftWatchdogBot/commit/209b6db97f33f79549864abcc1ba47fedc696e33))

## [1.1.1](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.1.0...v1.1.1) (2025-11-10)


### Bug Fixes

* docker monitoring ([331319f](https://github.com/Ranoth/MinecraftWatchdogBot/commit/331319f301b6c5310fefa7ec5f6de17b3f9f40f1))

## [1.1.0](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.0.1...v1.1.0) (2025-11-10)


### Features

* Add error messages for users ([d6d638a](https://github.com/Ranoth/MinecraftWatchdogBot/commit/d6d638adfdb2d00e61a2592feaac4190fc370b58))
* Add status command that runs tick query ([d6d638a](https://github.com/Ranoth/MinecraftWatchdogBot/commit/d6d638adfdb2d00e61a2592feaac4190fc370b58))

## [1.0.1](https://github.com/Ranoth/MinecraftWatchdogBot/compare/v1.0.0...v1.0.1) (2025-11-10)


### Bug Fixes

* reference docker_monitor.py in Dockerfile ([803a216](https://github.com/Ranoth/MinecraftWatchdogBot/commit/803a21614154fc9a47f88434e56c89f669b46341))

## 1.0.0 (2025-11-10)


### Bug Fixes

* ci ([39e35e9](https://github.com/Ranoth/MinecraftWatchdogBot/commit/39e35e9be147096011f8b5a4c9cd1e641a780079))
* ci ([dbd6e40](https://github.com/Ranoth/MinecraftWatchdogBot/commit/dbd6e407cd310952e6ec1344bd07de5053d294d0))
* ci ([f4179bd](https://github.com/Ranoth/MinecraftWatchdogBot/commit/f4179bd9c147c3c59ab6d220354e2cb079630d06))
* implement CI ([ea523f8](https://github.com/Ranoth/MinecraftWatchdogBot/commit/ea523f8792d83fe9e9ed97086255b9fdbdbe32b5))
* Trigger CI/CD pipeline ([14bc60d](https://github.com/Ranoth/MinecraftWatchdogBot/commit/14bc60d8221e83717f3ec0118889e02f1566cdd7))
* Trigger CI/CD pipeline ([7d5f91a](https://github.com/Ranoth/MinecraftWatchdogBot/commit/7d5f91aa3d9f4c6c1e9111066e4745eba5676d68))
* Trigger CI/CD pipeline ([8eae504](https://github.com/Ranoth/MinecraftWatchdogBot/commit/8eae504f102bb47643c4483a0552cb95fd37e406))
