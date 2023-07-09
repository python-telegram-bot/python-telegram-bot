Stability Policy
================

.. important::

    This stability policy is in place since version 20.3.
    While earlier versions of ``python-telegram-bot`` also had stable interfaces, they had no explicit stability policy and hence did not follow the rules outlined below in all detail.
    Please also refer to the :ref:`changelog <ptb-changelog>`.

.. caution::

    Large parts of the :mod:`telegram` package are the Python representations of the Telegram Bot API, whose stability policy PTB can not influence.
    This policy hence includes some special cases for those parts.

What does this policy cover?
----------------------------

This policy includes any API or behavior that is covered in this documentation.
This covers both the :mod:`telegram` package and the :mod:`telegram.ext` package.

What doesn't this policy cover?
-------------------------------

Introduction of new features or changes of flavors of comparable behavior (e.g. the default for the HTTP protocol version being used) are not covered by this policy.

The internal structure of classes in PTB, i.e. things like the result of ``dir(obj))`` or the contents of ``obj.__dict__``, is not covered by this policy.

Objects are in general not guaranteed to be pickleable (unless stated otherwise) and pickled objects from one version of PTB may not be loadable in future versions.
We may provide a way to convert pickled objects from one version to another, but this is not guaranteed.

Functionality that is part of PTBs API but is explicitly documented as not being intended to be used directly by users (e.g. :meth:`telegram.request.BaseRequest.do_request`) may change.
This also applies to functions or attributes marked as final in the sense of `PEP 591 <https://peps.python.org/pep-0591/>`__.

PTB has dependencies to third-party packages.
The versions that PTB uses of these third-party packages may change if that does not affect PTBs public API.

PTB does not give guarantees about which Python versions are supported.
In general, we will try to support all Python versions that have not yet reached their end of life, but we reserve ourselves the option to drop support for Python versions earlier if that benefits the advancement of the library.

PTB provides static type hints for all public attributes, parameters, return values and generic classes.
These type hints are not covered by this policy and may change at any time under the condition that these changes have no impact on the runtime behavior of PTB.

.. _bot-api-functionality-1:

Bot API Functionality
~~~~~~~~~~~~~~~~~~~~~

Comparison of equality of instances of the classes in the :mod:`telegram` package is subject to change and the PTB team will update the behavior to best reflect updates in the Bot API.
Changes in this regard will be documented in the affected classes.
Note that equality comparison with objects that where serialized by an older version of PTB may hence give unexpected results.

When the order of arguments of the Bot API methods changes or they become optional/mandatory due to changes in the Bot API, PTB will always try to reflect these changes.
While we try to make such changes backward compatible, this is not always possible or only with significant effort.
In such cases we will find a trade-off between backward compatibility and fully complying with the Bot API, which may result in breaking changes.
We highly recommend using keyword arguments, which can help make such changes non-breaking on your end.

..
    We have documented a few common cases and possible backwards compatible solutions in the wiki as a reference for the dev team: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Bot-API-Backward-Compatibility

When the Bot API changes attributes of classes, the method :meth:`telegram.TelegramObject.to_dict` will change as necessary to reflect these changes.
In particular, attributes deprecated by Telegram will be removed from the returned dictionary.
Deprecated attributes that are still passed by Telegram will be available in the :attr:`~telegram.TelegramObject.api_kwargs` dictionary as long as PTB can support that with feasible effort.
Since attributes of the classes in the :mod:`telegram` package are not writable, we may change them to properties where appropriate.

Development Versions
~~~~~~~~~~~~~~~~~~~~

Pre-releases marked as alpha, beta or release candidate are not covered by this policy.
Before a feature is in a stable release, i.e. the feature was merged into the ``master`` branch but not released yet (or only in a pre-release), it is not covered by this policy either and may change.

Security
~~~~~~~~

We make exceptions from our stability policy for security.
We will violate this policy as necessary in order to resolve a security issue or harden PTB against a possible attack.

Versioning
----------

PTB uses a versioning scheme that roughly follows `https://semver.org/ <https://semver.org/>`_, although it may not be quite as strict.

Given a version of PTB X.Y.Z,

-  X indicates the major version number.
   This is incremented when backward incompatible changes are introduced.
-  Y indicates the minor version number.
   This is incremented when new functionality or backward compatible changes are introduced by PTB.
   *This is also incremented when PTB adds support for a new Bot API version, which may include backward incompatible changes in some cases as outlined* :ref:`below <bot-api-versioning>`.
-  Z is the patch version.
   This is incremented if backward compatible bug fixes or smaller changes are introduced.
   If this number is 0, it can be omitted, i.e. we just write X.Y instead of X.Y.0.

Deprecation
~~~~~~~~~~~

From time to time we will want to change the behavior of an API or remove it entirely, or we do so to comply with changes in the Telegram Bot API.
In those cases, we follow a deprecation schedule as detailed below.

Functionality is marked as deprecated by a corresponding note in the release notes and the documentation.
Where possible, a :class:`~telegram.warnings.PTBDeprecationWarning` is issued when deprecated functionality is used, but this is not mandatory.

From time to time, we may decide to deprecate an API that is particularly widely used.
In these cases, we may decide to provide an extended deprecation period, at our discretion.

With version 20.0.0, PTB introduced major structural breaking changes without the above deprecation period.
Should a similarly big change ever be deemed necessary again by the development team and should a deprecation period prove too much additional effort, this violation of the stability policy will be announced well ahead of the release in our channel, `as was done for v20 <https://t.me/pythontelegrambotchannel/94>`_.

Non-Bot API Functionality
#########################

Starting with version 20.3, deprecated functionality will stay available for the current and the next major version.
For example:

-  In PTB v20.1.1 the feature exists
-  In PTB v20.1.2 or v20.2.0 the feature is marked as deprecated
-  In PTB v21.*.* the feature is marked as deprecated
-  In PTB v22.0 the feature is removed or changed

.. _bot-api-versioning:

Bot API Functionality
#####################

As PTB has no control over deprecations introduced by Telegram and the schedule of these deprecations rarely coincides with PTBs deprecation schedule, we have a special policy for Bot API functionality.

Starting with 20.3, deprecated Bot API functionality will stay available for the current and the next major version of PTB *or* until the next version of the Bot API.
More precisely, two cases are possible, for which we show examples below.

Case 1
^^^^^^

-  In PTB v20.1 the feature exists
-  Bot API version 6.6 is released and deprecates the feature
-  PTB v20.2 adds support for Bot API 6.6 and the feature is
   marked as deprecated
-  In PTB v21.0 the feature is removed or changed

Case 2
^^^^^^

-  In PTB v20.1 the feature exists
-  Bot API version 6.6 is released and deprecates the feature
-  PTB v20.2 adds support for Bot API version 6.6 and the feature is marked as deprecated
-  In PTB v20.2.* and v20.3.* the feature is marked as deprecated
-  Bot API version 6.7 is released
-  PTB v20.4 adds support for Bot API version 6.7 and the feature is removed or changed
