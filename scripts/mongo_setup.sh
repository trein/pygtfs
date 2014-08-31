#!/usr/bin/env bash
mongoimport --db pygtfs --collection direction --file ../extras/db/direction.json
mongoimport --db pygtfs --collection drop_off_type --file ../extras/db/dropofftype.json
mongoimport --db pygtfs --collection exception_type --file ../extras/db/exceptiontype.json
mongoimport --db pygtfs --collection payment_method --file ../extras/db/paymentmethod.json
mongoimport --db pygtfs --collection pickup_type --file ../extras/db/pickuptype.json
mongoimport --db pygtfs --collection route_type --file ../extras/db/routetype.json
mongoimport --db pygtfs --collection wheelchair_accessible --file ../extras/db/wheelchairaccessible.json
