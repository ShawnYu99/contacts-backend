from flask import Flask, send_file, jsonify, request
from flask_cors import CORS
from flask_restx import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)
api = Api(app, version='1.0', title='REST API for contact')
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'


# design a database for contacts
class ContactsDB(db.Model):
    name = db.Column(db.String, nullable=False, primary_key=True, unique=True)
    phoneNumber = db.Column(db.String, nullable=False)

    def __repr__(self):
        return self.name


# post request for adding new contact
contact_post_req = reqparse.RequestParser()
# get request for adding new contact
contact_get_req = reqparse.RequestParser()
# get request for updating a contact
contact_edit_req = reqparse.RequestParser()
contact_edit_req.add_argument('name', type=str, action='split')
# get request for delete a contact
contact_delete_req = reqparse.RequestParser()


@api.route('/contacts')
class Contacts(Resource):
    @api.doc(description='Get all contacts')
    @api.response(200, 'OK')
    @api.expect(contact_get_req)
    def get(self):
        contacts_query = ContactsDB.query.all()
        data = []
        for i in contacts_query:
            contactData = {}
            contactData['name'] = i.name
            contactData['mobile'] = i.phoneNumber
            data.append(contactData)
        return data


@api.route('/contact')
class Contact(Resource):
    @api.doc(description='Add a new contact')
    @api.response(201, 'Created')
    @api.expect(contact_post_req)
    def post(self):
        data = api.payload
        name = data['name']
        number = data['mobile']
        # add new contact into database
        newContact = ContactsDB(name=name, phoneNumber=number)
        db.session.add(newContact)
        db.session.commit()
        # return information
        res = {
            'name': name,
            'mobile': number
        }
        return res


@api.route('/contact/edit')
class Contact(Resource):
    @api.doc(description='Update contact information')
    @api.response(200, 'OK')
    @api.expect(contact_edit_req)
    def put(self):
        args = contact_edit_req.parse_args()
        name = args['name'][1]
        info = api.payload
        newName = info['name']
        newMobile = info['mobile']
        contact = ContactsDB.query.get_or_404(name)
        db.session.delete(contact)
        db.session.commit()
        newContact = ContactsDB(name=newName, phoneNumber=newMobile)
        db.session.add(newContact)
        db.session.commit()
        data = {
            'message': f'Update success'
        }
        return data

    @api.doc(description='Delete a contact')
    @api.response(200, 'OK')
    @api.expect(contact_delete_req)
    def delete(self):
        info = api.payload
        name = info['name']
        print(name)
        contact = ContactsDB.query.get_or_404(name)
        db.session.delete(contact)
        db.session.commit()
        data = {
            'message': f"{name} deleted"
        }
        return data


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=3000)
