import os
import pyttsx3
from time import localtime, strftime

# pdf
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

# epub
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

# pptx
# from pptx import Presentation


LIST_EXTENSIONS = ["txt", "pdf", "docx", "md", "epub"]

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')

temp_text = ""
current_path = os.path.abspath(os.getcwd())


def convert(text, lang, save, input_type=None, start=None, end=None):
    temp_text = text
    if LIST_EXTENSIONS[input_type - 1] == "pdf":
        temp_text = convert_pdf(text, start, end)
    elif LIST_EXTENSIONS[input_type - 1] == "epub":
        temp_text = convert_epub(text, start, end)
    if input_type:
        os.remove(f"{current_path}\\static\\temp_saved_files\\{text}")
    for voice in voices:
        if "Bart" in voice.name and lang == 'be':
            engine.setProperty('voice', voice.id)
            engine.setProperty('rate', 180)
        elif "Richard" in voice.name and lang == 'en':
            engine.setProperty('voice', voice.id)
            engine.setProperty('rate', 169)
    if save != None:
        current_time = strftime('%d-%m-%YT%H%M%S', localtime())
        if input_type == None:
            engine.save_to_file(
                temp_text, f"text_to_speech_{current_time}.mp3")
        else:
            file_name = text.rsplit(".", 1)[0]
            engine.save_to_file(
                temp_text, f"{file_name}.mp3")
    else:
        engine.say(temp_text)
    engine.runAndWait()
    if save != None:
        os.rename(f"{current_path}\\text_to_speech_{current_time}.mp3",
                  f"{current_path}\\speech\\text_to_speech_{current_time}.mp3")
    return True


def convert_pdf(text, start, end):
    if bool(start) and bool(end) and int(start) > int(end):
        if bool(end):
            return "Start page needs to be less than end page!"
    output_string = StringIO()
    with open(f"{current_path}\\static\\temp_saved_files\\{text}", 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(
            rsrcmgr, output_string, laparams=LAParams())
        intrepreter = PDFPageInterpreter(
            rsrcmgr, device)
        for index, page in enumerate(PDFPage.create_pages(doc)):
            if bool(end) and index > int(end):
                return temp_text
            if bool(start) and index + 1 >= int(start):
                intrepreter.process_page(page)
            elif bool(start) and index + 1 < int(start):
                continue
            else:
                intrepreter.process_page(page)
    return output_string.getvalue()


def convert_epub(text, start, end):
    if bool(start) and bool(end) and int(start) > int(end):
        if bool(end):
            return "Start page needs to be less than end page!"
    book = epub.read_epub(
        f"{current_path}\\static\\temp_saved_files\\{text}")
    temp_text = ""
    index = 0
    for item in book.get_items():
        print("i", index)
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            if bool(end) and index > int(end):
                return temp_text
            if bool(start) and index + 1 >= int(start):
                soup = BeautifulSoup(item.get_content())
                temp_text += soup.get_text('\n')
            elif bool(start) and index + 1 < int(start):
                index += 1
                continue
            else:
                soup = BeautifulSoup(item.get_content())
                temp_text += soup.get_text('\n')
            index += 1
    return temp_text
