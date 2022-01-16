# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.cloud import firestore

def document_to_dict(doc):
    if not doc.exists:
        return None
    doc_dict = doc.to_dict()
    doc_dict['id'] = doc.id
    return doc_dict


def next_page(limit=10, start_after=None):
    db = firestore.Client()

    query = db.collection(u'Data').limit(limit).order_by(u'time')

    if start_after:
        # Construct a new query starting at this document.
        query = query.start_after({u'time': start_after})

    docs = query.stream()
    docs = list(map(document_to_dict, docs))

    last_title = None
    if limit == len(docs):
        # Get the last document from the results and set as the last title.
        last_title = docs[-1][u'time']
    return docs, last_title


def read(data_id):
    db = firestore.Client()
    data_ref = db.collection(u'Data').document(data_id)
    snapshot = data_ref.get()
    return document_to_dict(snapshot)


def update(data, data_id=None):
    db = firestore.Client()
    data_ref = db.collection(u'Data').document(data_id)
    data_ref.set(data)
    return document_to_dict(data_ref.get())


create = update


def delete(id):
    db = firestore.Client()
    data_ref = db.collection(u'Data').document(id)
    data_ref.delete()

def highest_sensor(sensor):
    db = firestore.Client()
    docs = db.collection(u'Data').order_by(sensor, direction=firestore.Query.DESCENDING).limit(1).stream()
    return list(map(document_to_dict, docs))[0]

def latest_values():
    db = firestore.Client()
    docs = db.collection(u'Data').order_by("time", direction=firestore.Query.DESCENDING).limit(1).stream()
    return list(map(document_to_dict, docs))[0]

