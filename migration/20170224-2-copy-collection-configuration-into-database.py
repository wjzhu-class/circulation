#!/usr/bin/env python
"""Copy the collection configuration information from the JSON configuration
into Collection objects.
"""

import os
import sys
import uuid
from pdb import set_trace
bin_dir = os.path.split(__file__)[0]
package_dir = os.path.join(bin_dir, u"..")
sys.path.append(os.path.abspath(package_dir))
from api.config import Configuration
from core.model import (
    get_one_or_create,
    production_session,
    Collection,
    ExternalIntegration,
    Library,
)

# We're going directly against the configuration object, rather than
# using shortcuts like OverdriveAPI.from_environment, because this
# script may be running against a branch where the implementation of
# those shortcuts goes against the database.

_db = production_session()

def copy_library_registry_information(_db, library):
    config = Configuration.integration("Adobe Vendor ID")
    if not config:
        print u"No Adobe Vendor ID configuration, not setting short name or secret."
    library.short_name = config.get("library_short_name")
    library.library_registry_short_name = config.get("library_short_name")
    library.library_registry_shared_secret = config.get("authdata_secret")


def convert_overdrive(_db, library):
    config = Configuration.integration('Overdrive')
    if not config:
        print u"No Overdrive configuration, not creating a Collection for it."
        return
    print u"Creating Collection object for Overdrive collection."
    username = config.get('client_key')
    password = config.get('client_secret')
    library_id = config.get('library_id')
    website_id = config.get('website_id')

    collection, ignore = get_one_or_create(_db, Collection, name=u"Overdrive")
    collection.external_account_id = library_id
    library.collections.append(collection)

    integration = collection.create_external_integration(
        ExternalIntegration.OVERDRIVE
    )
    integration.username = username
    integration.password = password
    integration.set_setting(u"website_id", website_id)

def convert_bibliotheca(_db, library):
    config = Configuration.integration('3M')
    if not config:
        print u"No Bibliotheca configuration, not creating a Collection for it."
        return
    print u"Creating Collection object for Bibliotheca collection."
    username = config.get('account_id')
    password = config.get('account_key')
    library_id = config.get('library_id')
    collection, ignore = get_one_or_create(_db, Collection, name=u"Bibliotheca")
    collection.external_account_id = library_id
    library.collections.append(collection)

    integration = collection.create_external_integration(
        ExternalIntegration.BIBLIOTHECA
    )
    integration.username = username
    integration.password = password

def convert_axis(_db, library):
    config = Configuration.integration('Axis 360')
    if not config:
        print u"No Axis 360 configuration, not creating a Collection for it."
        return
    print u"Creating Collection object for Axis 360 collection."
    username = config.get('username')
    password = config.get('password')
    library_id = config.get('library_id')
    # This is not technically a URL, it's u"production" or u"staging",
    # but it's converted into a URL internally.
    url = config.get('server')
    collection, ignore = get_one_or_create(_db, Collection, name=u"Axis 360")
    collection.external_account_id = library_id
    library.collections.append(collection)

    integration = collection.create_external_integration(
        ExternalIntegration.AXIS_360
    )
    integration.username = username
    integration.password = password
    integration.url = url

def convert_one_click(_db, library):
    config = Configuration.integration('OneClick')
    if not config:
        print u"No OneClick configuration, not creating a Collection for it."
        return
    print u"Creating Collection object for OneClick collection."
    basic_token = config.get('basic_token')
    library_id = config.get('library_id')
    url = config.get('url')
    ebook_loan_length = config.get('ebook_loan_length')
    eaudio_loan_length = config.get('eaudio_loan_length')
    
    collection, ignore = get_one_or_create(_db, Collection, name=u"OneClick")
    collection.external_account_id = library_id
    library.collections.append(collection)

    integration = collection.create_external_integration(
        ExternalIntegration.ONE_CLICK
    )
    integration.password = basic_token
    integration.url = url
    
def convert_content_server(_db, library):
    config = Configuration.integration("Content Server")
    if not config:
        print u"No content server configuration, not creating a Collection for it."
        return
    url = config.get('url')
    collection, ignore = get_one_or_create(
        _db, Collection, name=u"Open Access Content Server"
    )
    collection.external_account_id = url
    library.collections.append(collection)
    integration = collection.create_external_integration(
        ExternalIntegration.OPDS_IMPORT
    )

# This is the point in the migration where we first create a Library
# for this system.
library, ignore = get_one_or_create(
    _db, Library,
    create_method_kwargs=dict(
        name="Default Library",
        short_name="default",
        uuid=unicode(uuid.uuid4())
    )
)

copy_library_registry_information(_db, library)
convert_overdrive(_db, library)
convert_bibliotheca(_db, library)
convert_axis(_db, library)
convert_one_click(_db, library)
convert_content_server(_db, library)
_db.commit()
