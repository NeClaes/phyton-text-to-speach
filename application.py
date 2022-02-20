from flask import Flask, flash, request, redirect, render_template, url_for
import os
import multiprocessing
import text_to_speach

app = Flask(__name__)

LIST_EXTENSIONS = ["txt", "pdf", "docx", "md", "epub"]
LIST_EMBEDED_TYPE = ["text/plain", "application/pdf",
                     "application/vnd.ms-word.document.macroEnabled.12", "text/markdown", "application/epub+zip"]
ALLOWED_EXTENSIONS = set(LIST_EXTENSIONS)
UPLOAD_FOLDER = "static/temp_saved_files/"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def num_file_typ(x):
    return LIST_EXTENSIONS.index(x) + 1


def get_input_type(x):
    return LIST_EMBEDED_TYPE[x - 1]


def check_proc(proc_name):
    active_proc = multiprocessing.active_children()
    for x in active_proc:
        if x.name == proc_name:
            x.terminate()


def start_proc(elements, name):
    proc = multiprocessing.Process(
        target=run_text_to_speach, name=name, kwargs=elements)
    proc.start()


def run_text_to_speach(queue, input_type, text, lang, save, start=None, end=None):
    if input_type == 0:
        is_converted = text_to_speach.convert(text, lang, save)
        print(is_converted)
        if is_converted:
            queue.put(True)
    if input_type > 0:
        is_converted = text_to_speach.convert(
            text, lang, save, input_type, start, end)
        if is_converted:
            queue.put(True)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        proc_name = "proc_text_to_speech"
        # When the convertion needs to be stopped
        if "stop_convertion" in request.form:
            check_proc(proc_name)
        # Get Form values
        selected_text = request.form.get("selected_text")
        selected_file = request.files.get("selected_file")
        start_page = request.form.get("start_page")
        end_page = request.form.get("end_page")
        selected_lang = request.form.get("lang")
        selected_save = request.form.get("save")
        # Check if a text or document is send
        if not bool(selected_file) and not bool(selected_text):
            return render_template("index.html")
        else:
            # When a text is send
            if bool(selected_text):
                # maka queue object for when file is made
                q = multiprocessing.Queue()
                # Check if the file already is running a convertion
                check_proc(proc_name)
                # Start running file for convertion
                start_proc({'queue': q, 'input_type': 0, 'text': selected_text,
                            'lang': selected_lang, "save": selected_save}, proc_name)
                # return form when file is made
                if q.get and selected_save:
                    return render_template("index.html", text="File is made", input_type=None, converted=True)
                # return the text that wil be converted
                if selected_save == None:
                    return render_template("index.html", text=selected_text, input_type=None)
                else:
                    return render_template("index.html", text=selected_text, input_type=None, disable_input=True)
            # When a document is send
            elif bool(selected_file):
                print(selected_file.filename)
                if allowed_file(selected_file.filename):
                    file_ext = selected_file.filename.rsplit(".", 1)[1].lower()
                    file_type = num_file_typ(file_ext)
                    input_type = get_input_type(file_type)
                    print(file_type)
                    selected_file.save(os.path.join(
                        UPLOAD_FOLDER, selected_file.filename))
                    file_path = os.path.join(
                        UPLOAD_FOLDER, selected_file.filename)
                    # maka queue object for when file is made
                    q = multiprocessing.Queue()
                    # Check if the file already is running a convertion
                    check_proc(proc_name)
                    # Start running file for convertion
                    start_proc({'queue': q, 'input_type': file_type, 'text': selected_file.filename,
                                'lang': selected_lang, "save": selected_save, "start": start_page, "end": end_page}, proc_name)
                    # return form when file is made
                    if q.get and selected_save:
                        return render_template("index.html", text="File is made", input_type=None, converted=True)
                    # return the text that wil be converted
                    if selected_save == None:
                        return render_template("index.html", text=selected_text, input_type=input_type, src=file_path)
                    else:
                        return render_template("index.html", text=selected_text, input_type=input_type, src=file_path, disable_input=True)
                return render_template("index.html")

    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(threaded=True)
