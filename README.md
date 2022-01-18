# Data collection backend for Internet of Things on Google App Engine

Collection and aggregation of data from a large number of sensors is a common part of many Internet of Things applications. An IoT backend typically collects data, stores it in a database and performs some analysis on it, like aggregating the data by calculating averages, minima, maxima, etc. The objective of this project is to implement a backend on top of Google App Engine and Google Datastore that accepts data sent by sensors via a REST API, stores it in the Datastore, computes aggregates and provides simple dashboard that enables a user to view the data and the computed aggregates.

