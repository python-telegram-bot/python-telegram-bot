Stability Policy
================

The ``python-telegram-bot`` library (PTB) tries to provides a stable interface to its users.
As both the user base and the complexity of the library has grown significantly since PTBs conception, we introduced below explicit stability Policy with version NEXT.VERSION.

Large parts of the :mod:`telegram` package are the Python representations of the Telegram Bot API, the stability policy of which PTB can not influence.
This policy hence includes some special cases for those parts.

What does this policy cover?
----------------------------

This policy includes any API or behavior that is documented in this documentation.
This covers both the :mod:`telegram` package and the :mod:`telegram.ext` package.

What doesn't this policy cover?
-------------------------------

Introduction of new features or changes of flavors of comparable behavior (e.g. the default for the used HTTP protocol version) are not covered by this policy.
The internal structure of classes in PTB, i.e. things like the result of ``dir(obj))`` or the contents of ``obj.__dict__``, may change.

Objects are in general not guaranteed to be pickleable (unless stated otherwise) and pickled objects from one version of PTB may not be loadable in future versions.
We may provide a way to convert pickled objects from one version to another, but this is not guaranteed.

-  ☐ Document pickle stability for :class:`~telegram.TelegramObject` and error classes

Functionality that is part of PTBs API but is explicitly documented to not be intended to be used directly by users (e.g. :meth:`telegram.request.BaseRequest.do_request`) may change.
This also applies to functions or attributes marked as final in the sense of `PEP 591 <https://www.python.org/dev/peps/pep-0591/>`__.

PTB has dependencies to 3rd party packages.
The versions that PTB uses of these 3rd party packages may change if that does not change PTBs public API.

PTB does not give guarantees about which Python versions are supported.
In general, we will try to support all Python versions that have not yet reached their end of life, but we reserve ourselves the option to drop support for Python versions earlier if that benefits the advancement of the library.

.. _bot-api-functionality-1:

Bot API Functionality
~~~~~~~~~~~~~~~~~~~~~

Comparison of equality of the classe in the :mod:`telegram` package is subject to change and the PTB team will update the behavior to best reflect updates in the Bot API.

When arguments of the Bot API methods change order or become optional/mandatory due to changes in the Bot API, PTB will always try to reflect these changes.
While we try to make such changes backwards compatible, this is not always possible or only with significant effort.
In such cases we will find a trade-off between backwards compatibility and fully complying with the Bot API, which may result in breaking changes.
We highly recommend using keyword arguments, which can help to make such changes non-breaking on your end.

When the Bot API changes attributes of classes, the method :meth:`telegram.TelegramObject.to_dict` will change as necessary to reflect these changes.
In particular, attributes deprecated by Telegram will be removed from the returned dictionary.
Deprecated attributes that are still passed by Telegram will be available in the :attr:`~telegram.TelegramObject.api_kwargs` dictionary as long as PTB can support that with feasible effort.
Since attributes of the classes in the :mod:`telegram` package are not writable, we may change them to properties where appropriate.

Development Versions
~~~~~~~~~~~~~~~~~~~~

Before a feature is in a release, it is not covered by this policy and may change.
Pre-Release marked as alpha, beta or release candidate are not covered by this policy either.

Security
~~~~~~~~

We make exceptions from our stability policy for security.
We will violate this policy as necessary in order to resolve a security issue or harden PTB against a possible attack.

Versioning
----------

PTB uses a versioning scheme that roughly follows `https://semver.org/ <https://semver.org/>`_, although it may not be quite as strict.

Given a version of PTB X.Y.Z,

-  X indicates the major version number.
   This is incremented when backwards incompatible changes are introduced.
-  Y indicates the minor version number.
   This is incremented when new functionality or backwards compatible changes are introduced by PTB.
   *This is also incremented when PTB adds support for a new Bot API version, which may include backwards incompatible changes in some cases as outlined* :ref:`below <bot-api-versioning>`.
-  Z is the patch version.
   This is incremented if backwards compatible bug fixes or smaller changes are introduced.

Deprecation
~~~~~~~~~~~

From time to time we will want to change the behavior of an API or remove it entirely, or we do so to comply with changes in the Telegram Bot API.
In those cases, we follow a deprecation schedule as detailed below.

Functionality is marked as deprecated by a corresponding note in the release notes and the documentation.
Where possible, a :class:`~telegram.warnings.PTBDeprecationWarning` is issued when deprecated functionality is used, but this is not mandatory.

From time to time, we may decide to deprecate an API that is particularly widely used.
In these cases, we may decide to provide an extended deprecation period, at our discretion.

With version 20.0.0, PTB introduced majorly structural breaking changes without the above deprecation period.
Should a similarly big change ever be deemed necessary by the development team and should a deprecation period prove too much additional effort, this violation of the stability policy will be announced well ahead of the release in our channel.

Non-Bot API Functionality
#########################

Starting with version NEXT.VERSION, deprecated functionality will stay available for the current and the next major version.
More precisely:

-  In PTB X.Y.Z the feature exists
-  In PTB X.Y.(Z + 1) or X.(Y + 1).* the feature is marked as deprecated
-  In PTB (X + 1).*.* the feature is marked as deprecated
-  In PTB (X + 2).0.0 the feature is removed or changed

.. _bot-api-versioning:

Bot API Functionality
#####################

As PTB has no control over deprecations introduced by Telegram and the schedule of these deprecations rarely coincides with PTBs deprecation schedule, we have a special policy for Bot API functionality.

Starting with NEXT.VERSION, deprecated Bot API functionality will stay available for the current and the next major version *or* until the next version of the Bot API.
More precisely, two cases are possible.

Case 1
^^^^^^

-  In PTB X.Y.Z the feature exists
-  Bot API version N.M is released and deprecates the feature
-  In PTB X.(Y + 1).0 adds support for Bot API A.B and the feature is
   marked as deprecated
-  In PTB (X + 1).0.0 the feature is removed or changed

Case 2
^^^^^^

-  In PTB X.Y.Z the feature exists
-  Bot API version N.M is released and deprecates the feature
-  PTB X.(Y + 1).0 adds support for Bot API N.M and the feature is marked as deprecated
-  Bot API version N.(M + 1) is released
-  In PTB X.(Y + 2).0 adds support for Bot API N.(M + 1) and the feature is removed or changed