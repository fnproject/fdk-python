# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from fdk import headers


def test_push_header():
    cases = [
        ({}, "k", "v", {"k": "v"}),
        ({}, "k", ["v1", "v2"], {"k": ["v1", "v2"]}),
        ({"k": "v1"}, "k", "v2", {"k": ["v1", "v2"]}),
        ({"k": ["v1"]}, "k", "v2", {"k": ["v1", "v2"]}),
        ({"k": ["v1"]}, "k", ["v2"], {"k": ["v1", "v2"]}),
        ({"k": []}, "k", [], {"k": []}),
        ({"k": ["v1"]}, "k", [], {"k": ["v1"]}),
        ({"k": []}, "k", ["v1"], {"k": ["v1"]}),
        ({"k": "v1"}, "k", ["v2", "v3"], {"k": ["v1", "v2", "v3"]}),
        ({"k1": "v1"}, "k2", "v2", {"k1": "v1", "k2": "v2"}),

    ]

    for case in cases:
        initial = case[0]
        working = initial.copy()
        key = case[1]
        value = case[2]
        result = case[3]
        headers.push_header(working, key, value)
        assert working == result, "Adding  %s:%s to %s" \
                                  % (key, value, initial)


def test_encap_no_headers():
    encap = headers.encap_headers({})
    assert not encap, "headers should be empty"


def test_encap_simple_headers():
    encap = headers.encap_headers({
        "Test-header": "foo",
        "name-Conflict": "h1",
        "name-conflict": "h2",
        "nAme-conflict": ["h3", "h4"],
        "fn-http-h-name-conflict": "h5",
        "multi-header": ["bar", "baz"]
    })
    assert "fn-http-h-test-header" in encap
    assert "fn-http-h-name-conflict" in encap
    assert "fn-http-h-multi-header" in encap

    assert encap["fn-http-h-test-header"] == "foo"
    assert set(encap["fn-http-h-name-conflict"]) == {"h1", "h2",
                                                     "h3", "h4", "h5"}
    assert encap["fn-http-h-multi-header"] == ["bar", "baz"]


def test_encap_status():
    encap = headers.encap_headers({}, 202)
    assert "fn-http-status" in encap
    assert encap["fn-http-status"] == "202"


def test_encap_status_override():
    encap = headers.encap_headers({"fn-http-status": 412}, 202)
    assert "fn-http-status" in encap
    assert encap["fn-http-status"] == "202"


def test_content_type_version():
    encap = headers.encap_headers({"content-type": "text/plain",
                                   "fn-fdk-version": "1.2.3"})

    assert encap == {"content-type": "text/plain", "fn-fdk-version": "1.2.3"}


def test_decap_headers_merge():
    decap = headers.decap_headers({"fn-http-h-Foo-Header": "v1",
                                   "fn-http-h-merge-header": "v2",
                                   "fn-http-h-merge-Header": ["v3"],
                                   "Foo-Header": "ignored",
                                   "other-header": "bob"}, True)
    assert "foo-header" in decap
    assert decap["foo-header"] == "v1"

    assert "other-header" in decap
    assert decap["other-header"] == "bob"

    assert "merge-header" in decap
    assert set(decap["merge-header"]) == {"v2", "v3"}


def test_decap_headers_strip():
    decap = headers.decap_headers({"fn-http-h-Foo-Header": "v1",
                                   "fn-http-h-merge-header": ["v2"],
                                   "Foo-Header": "ignored",
                                   "merge-header": "v3",
                                   "other-header": "bad"}, False)
    assert decap == {"foo-header": "v1", "merge-header": ["v2"]}
