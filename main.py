from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import NameObject, TextStringObject
import os

import requests

class PDFFormFiller:
    def __init__(self, pdf_path, api_endpoint):
        self.pdf_path = pdf_path
        self.api_endpoint = api_endpoint

    def fetch_data_from_api(self):
        response = requests.get(self.api_endpoint)
        data = response.json()
        return data

    def find_fields_in_pdf(self):
        fields = []
        reader = PdfReader(self.pdf_path)
        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            annotations = page.get('/Annots')
            if annotations:
                for annotation in annotations:
                    field = annotation.get_object()
                    if '/T' in field:
                        # fields.append(field['/T'][1:])  # Remove leading '/'
                        fields.append(field['/T'])
        return fields

    def update_pdf(self, api_data):
        reader = PdfReader(self.pdf_path)
        writer = PdfWriter()

        for page_number in range(len(reader.pages)):
            page = reader.pages[page_number]
            annotations = page['/Annots']
            if annotations:
                for annotation in annotations:
                    annotation_object = annotation.get_object()
                    # field_name = annotation_object['/T'][1:]  # Remove leading '/'
                    field_name = annotation_object['/T']
                    if field_name in api_data:
                        annotation_object.update({NameObject("/V"): TextStringObject(api_data[field_name])})
            writer.add_page(page)

        with open("output/output.pdf", "wb") as output_pdf:
            writer.write(output_pdf)

    def fill_form(self):
        # api_data = self.fetch_data_from_api()
        api_data = {
            'Given Name Text Box': 'testnnnd',
            'Family Name Text Box': 'test family'
        }
        pdf_fields = self.find_fields_in_pdf()
        print(pdf_fields)
        self.update_pdf(api_data)

# Usage
os.makedirs('output', exist_ok=True)
pdf_form_filler = PDFFormFiller("input/input.pdf", "API_ENDPOINT_HERE")
pdf_form_filler.fill_form()