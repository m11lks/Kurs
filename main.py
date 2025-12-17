import mysql.connector
from stamp_objects import Album, Collection, Stamps, Pages
from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog, simpledialog
import xml.etree.ElementTree as ET
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import logging
from exceptionfile import *


logging.basicConfig(filename='stamp_collection.log', filemode='a', level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

def database_connection():
    try:
        logging.info("Connecting to database")
        cnx = mysql.connector.connect(user='root', password='12345',
                                      host='127.0.0.1',
                                      database='stamps_collection')
        logging.info("Successfully")
        return cnx
    
    except ValidationException as database_error:
        messagebox.showerror("Database Error", f"Cannot connect to database: {database_error}")
        return None
    
def database_album():
    cnx = database_connection()
    if not cnx:
        logging.warning("No database connection (albums)")
        return []
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT idalbum, name_of_album FROM album")
        albums = cursor.fetchall()
        album_objects = []
        for row in albums:
            album_obj = Album(int(row[0]), str(row[1]))
            collections = database_collection(album_obj.get_idalbum())
            for collection in collections:
                album_obj.set_collection_list(collection) 
            album_objects.append(album_obj)
        return album_objects
    except ValidationException as database_error:
        messagebox.showerror("Database Error", f"Cannot load albums: {database_error}")
        return []
    finally:
        if cnx:
            cursor.close()
            cnx.close()
            logging.debug("Database connection closed (albums)")

def database_collection(id_alb):
    cnx = database_connection()
    if not cnx:
        logging.warning("No database connection (collections)")
        return []
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT idcollection, name_of_collection, total_pages FROM collection WHERE idalbum = %s", (id_alb,))
        collections = cursor.fetchall()
        collection_objects = []
        for row in collections:
            collection_obj = Collection(int(row[0]), str(row[1]), int(row[2]))
            pages = database_pages(collection_obj.get_idcollection())
            for page in pages:
                collection_obj.set_pages_list(page)  
            collection_objects.append(collection_obj)
        return collection_objects
    except ValidationException as database_error:
        messagebox.showerror("Database Error", f"Cannot load collections: {database_error}")
        return []
    finally:
        if cnx:
            cursor.close()
            cnx.close()
            logging.debug("Database connection (collections)")

def database_pages(id_col):
    cnx = database_connection()
    if not cnx:
        logging.warning("No database connection (pages)")
        return []
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT idpages, number_of_page FROM pages WHERE idcollection = %s", (id_col,))
        pages = cursor.fetchall()
        pages_objects = []
        for row in pages:
            page_obj = Pages(int(row[0]), int(row[1]))
            stamps = database_stamp(page_obj.get_idpage())
            for stamp in stamps:
                page_obj.set_stamps_list(stamp)  
            pages_objects.append(page_obj)
        return pages_objects
    except ValidationException as database_error:
        messagebox.showerror("Database Error", f"Cannot load pages: {database_error}")
        return []
    finally:
        if cnx:
            cursor.close()
            cnx.close()
            logging.debug("Database connection closed (pages)")

def database_stamp(id_p):
    cnx = database_connection()
    if not cnx:
        logging.warning("No database connection (stamps)")
        return []
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT idstamp, country, name_of_stamp, year, series FROM stamps WHERE idpages = %s", (id_p,))
        stamps = cursor.fetchall()
        stamps_objects = []
        for row in stamps:
            stamp_obj = Stamps(int(row[0]), str(row[2]), str(row[1]), int(row[3]), str(row[4]))
            stamps_objects.append(stamp_obj)
            
        return stamps_objects
    except ValidationException as database_error:
        messagebox.showerror("Database Error", f"Cannot load stamps: {database_error}")
        return []
    finally:
        if cnx:
            cursor.close()
            cnx.close()
            logging.debug("Database connection closed (stamps)")

logging.info("Loading albums")
albums = database_album()

root = Tk()
root.title("Stamps_collection")
root.geometry("800x600") 
root.configure(bg='white')

try:
    logging.debug("Loading album logo")
    logo = PhotoImage(file=r"C:\Users\Admin\Desktop\stamp_collection\album2.png")
    logging.info("Logo loaded successfully")

except ValidationException as image_error:
    logging.warning(f"Cannot load logo image: {image_error}")
    messagebox.showwarning("Image Error", f"Cannot load image: {image_error}")
    logo = None  

content_frame = tk.Frame(root, bg='white')
content_frame.pack(fill=BOTH, expand=True) 

def clear_screen():
    logging.debug("Clearing screen")
    for widget in content_frame.winfo_children():
        widget.destroy()
    logging.debug("Screen cleared")

def open_pages(idcollection, name_of_collection):
    try:
        logging.info(f"Opening pages for collection: {name_of_collection} (ID: {idcollection})")
        clear_screen()
        label_pages = tk.Label(content_frame, text=f"Pages of {name_of_collection}", bg='white')
        label_pages.pack(pady=20)

        pages = database_pages(idcollection)
        
        if not pages:
            logging.warning(f"No pages found for collection {name_of_collection}")
            no_data_label = tk.Label(content_frame, text="No pages found", bg='white', fg='gray')
            no_data_label.pack()
            back_button = ttk.Button(content_frame, text="Back to albums", command=main_screen)
            back_button.pack(pady=30)
            return
        
        pages_frame = tk.Frame(content_frame, bg='white')
        pages_frame.pack(pady=30)

        for i, page in enumerate(pages):
            idpage = page.get_idpage()
            number_of_page = page.get_number_of_page()

            page_frame = tk.Frame(pages_frame, bg='white')
            
            row_index = i // 3  
            col_index = i % 3   
            
            page_frame.grid(row=row_index, column=col_index, padx=30, pady=10)

            page_label = tk.Label(page_frame, text=f"page {number_of_page}", bg='white')
            page_label.pack(pady=5)

            stamps_button = ttk.Button(page_frame, text="View Stamps", 
                                     command=lambda p_id=idpage, p_num=number_of_page, 
                                     c_id=idcollection, c_name=name_of_collection: 
                                     open_stamps(p_id, p_num, c_id, c_name))
            stamps_button.pack(pady=10)

        back_button = ttk.Button(content_frame, text="Back to albums", command=main_screen)
        back_button.pack(pady=30)
        logging.info(f"Pages view loaded successfully")

    except ValidationException as e:
        error_label = tk.Label(content_frame, text=f"Error: {str(e)}", bg='white', fg='red')
        error_label.pack()

def open_collection(idalbum, name_of_album, album_index):
    try:
        logging.info(f"Opening collection for album: {name_of_album} (ID: {idalbum})")
        clear_screen()  

        label_collection = tk.Label(content_frame, text=f"Collection of {name_of_album}", bg='white')
        label_collection.pack(pady=20)

        collections = database_collection(idalbum)
        
        collections_frame = tk.Frame(content_frame, bg='white')
        collections_frame.pack(pady=30)

        try:
            logging.debug("Loading collection images")
            image1 = PhotoImage(file=r"C:\Users\Admin\Desktop\stamp_collection\collection1.png")
            image2 = PhotoImage(file=r"C:\Users\Admin\Desktop\stamp_collection\collection2.png")
            image3 = PhotoImage(file=r"C:\Users\Admin\Desktop\stamp_collection\collection3.png")
            image4 = PhotoImage(file=r"C:\Users\Admin\Desktop\stamp_collection\collection4.png")
            image5 = PhotoImage(file=r"C:\Users\Admin\Desktop\stamp_collection\collection5.png")
            image6 = PhotoImage(file=r"C:\Users\Admin\Desktop\stamp_collection\collection6.png")
            images = [image1, image2, image3, image4, image5, image6]
            logging.info("Collection images loaded successfully")
        except ValidationException as image_error:
            logging.warning(f"Cannot load collection images: {image_error}")
            messagebox.showwarning("Image Error", f"Cannot load images: {image_error}")
            return
        
        image_album = album_index * 3

        for i, collection in enumerate(collections):
            idcollection = collection.get_idcollection()
            name_of_collection = collection.get_name_of_collection()
            total_pages = collection.get_total_pages()

            collection_frame = tk.Frame(collections_frame, bg='white')
            
            row_index = i // 3  
            col_index = i % 3   
            
            collection_frame.grid(row=row_index, column=col_index, padx=30, pady=10)
            image_index = (i + image_album) % 6
            collection_image = images[image_index]

            image_label = tk.Label(collection_frame, image=collection_image, bg='white')
            image_label.image = collection_image
            image_label.pack(pady=5)

            name_label = tk.Label(collection_frame, text=name_of_collection, bg='white')
            name_label.pack(pady=5)

            total_pages_label = tk.Label(collection_frame, text=f"total pages: {total_pages}", bg='white')
            total_pages_label.pack(pady=5)

            pages_button = ttk.Button(collection_frame, text="View pages", command=lambda c_id=idcollection, c_name=name_of_collection: open_pages(c_id, c_name))
            pages_button.pack(pady=10)

        back_button = ttk.Button(content_frame, text="Back to albums", command=main_screen)
        back_button.pack(pady=30)
        
    except ValidationException as collection_error:
        messagebox.showerror("Error", f"Cannot open collection: {collection_error}")
        main_screen()


def open_stamps(idpage, number_of_page, idcollection, name_of_collection):
    try:
        logging.info(f"Opening stamps for page {number_of_page} (ID: {idpage})")
        clear_screen()
        label_stamp = tk.Label(content_frame, text=f"Stamps", bg='white')
        label_stamp.pack(pady=20)

        stamps = database_stamp(idpage)
        
        if not stamps:
            logging.warning(f"No stamps found for page {number_of_page}")
            no_data_label = tk.Label(content_frame, text="No stamps found", bg='white', fg='gray')
            no_data_label.pack()
            back_button = ttk.Button(content_frame, text="Back to pages ", command=lambda: open_pages(idcollection, name_of_collection))
            back_button.pack(pady=30)
            return
            
        
        tree_frame = tk.Frame(content_frame, bg='white')
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
    
        columns = ("ID","Country", "Name", "Year", "Series")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        for stamp in stamps:
            tree.insert("", tk.END, values=(
            stamp.get_idstamp(),
            stamp.get_country(),
            stamp.get_name_of_stamp(),
            stamp.get_year(),
            stamp.get_series(),
        )
    )
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        back_button = ttk.Button(content_frame, text="Back to pages ", command=lambda: open_pages(idcollection, name_of_collection))
        back_button.pack(pady=30)
        logging.info(f"Stamps view loaded successfully")

    except ValidationException as e:
        error_label = tk.Label(content_frame, text=f"Error: {str(e)}", bg='white', fg='red')
        error_label.pack()

def export_to_xml():
    try:
        logging.info("Starting xml export")
        root = ET.Element('stamps_collection')
        file_path = filedialog.asksaveasfilename(
            title="Save XML file",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml")],
            initialfile="stamps_collection.xml"
        )

        if not file_path:
            logging.warning("XML export cancelled by user")
            return

        albums = database_album()
        
        for album in albums:
            idalbum = album.get_idalbum()
            name_of_album = album.get_name_of_album()

            album_el = ET.SubElement(root, 'album')
            album_el.set('id', str(idalbum))
            album_el.set('name', name_of_album)

            collections = database_collection(idalbum)
            for collection in collections:
                idcollection = collection.get_idcollection()
                name_of_collection = collection.get_name_of_collection()
                total_pages = collection.get_total_pages()

                collection_el = ET.SubElement(album_el, 'collection')
                collection_el.set('id', str(idcollection))
                collection_el.set('name', name_of_collection)
                collection_el.set('pages',str(total_pages))

                pages = database_pages(idcollection)
                for page in pages:
                    idpage = page.get_idpage()
                    number_of_page = page.get_number_of_page()


                    page_el = ET.SubElement(collection_el, 'pages')
                    page_el.set('id', str(idpage))
                    page_el.set('number', str(number_of_page))
                    
                    stamps = database_stamp(idpage)
                    for stamp in stamps:
                        idstamp = stamp.get_idstamp()
                        country = stamp.get_country()
                        year = stamp.get_year()
                        series = stamp.get_series()
                        name_of_stamp = stamp.get_name_of_stamp()

                        stamp_el = ET.SubElement(page_el, 'stamp')
                        stamp_el.set("id", str(idstamp))
                        ET.SubElement(stamp_el, 'country').text = str(country)
                        ET.SubElement(stamp_el, 'name').text = str(name_of_stamp)
                        ET.SubElement(stamp_el, 'year').text = str(year)
                        ET.SubElement(stamp_el, 'series').text = str(series)

        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        logging.info(f"XML export completed successfully: {file_path}")
        messagebox.showinfo("Success", "Data exported to stamps_collection.xml")

    except ValidationException as export_error:
        messagebox.showerror("Export error", f"Cannot export to XML: {export_error}")
        
def import_from_xml():
    try:
        logging.info("Starting XML import")
        file_path = filedialog.askopenfilename(
            title="Select XML file",
            filetypes=[("XML files", "*.xml")]
        )

        if not file_path:
            logging.warning("XML import cancelled by user")
            return
        
        cnx = database_connection()
        cursor = cnx.cursor()
        
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        for album_el in root.findall('album'):
            idalbum = album_el.get('id')
            name_of_album = album_el.get('name')
        
            cursor.execute("SELECT idalbum FROM album WHERE idalbum = %s", (idalbum,))
            if cursor.fetchone():
                cursor.execute("UPDATE album SET name_of_album = %s WHERE idalbum = %s", 
                             (name_of_album, idalbum))
                logging.debug(f"Updated album: {name_of_album}")
            else:
                cursor.execute("INSERT INTO album (idalbum, name_of_album) VALUES (%s, %s)", 
                             (idalbum, name_of_album))
                logging.debug(f"Inserted new album: {name_of_album}")
            
            for collection_el in album_el.findall('collection'):
                idcollection = collection_el.get('id')
                name_of_collection = collection_el.get('name')
                total_pages = collection_el.get('total_pages', 0)
                
                cursor.execute("SELECT idcollection FROM collection WHERE idcollection = %s", (idcollection,))
                if cursor.fetchone():
                    cursor.execute("UPDATE collection SET name_of_collection = %s, total_pages = %s, idalbum = %s WHERE idcollection = %s",
                                 (name_of_collection, total_pages, idalbum, idcollection))
                    logging.debug(f"Updated collection: {name_of_collection}")
                else:
                    cursor.execute("INSERT INTO collection (idcollection, name_of_collection, total_pages, idalbum) VALUES (%s, %s, %s, %s)", 
                                 (idcollection, name_of_collection, total_pages, idalbum))
                    logging.debug(f"Inserted new collection: {name_of_collection}")

                for page_el in collection_el.findall('page'):
                    idpage = page_el.get('id')
                    number_of_page = page_el.get('number')
                    
                    cursor.execute("SELECT idpages FROM pages WHERE idpages = %s", (idpage,))
                    if cursor.fetchone():
                        cursor.execute("UPDATE pages SET number_of_page = %s, idcollection = %s WHERE idpages = %s", 
                                     (number_of_page, idcollection, idpage))
                    else:
                        cursor.execute("INSERT INTO pages (idpages, number_of_page, idcollection) VALUES (%s, %s, %s)", 
                                     (idpage, number_of_page, idcollection))

                    for stamp_el in page_el.findall('stamp'):
                        idstamp = stamp_el.get('id')
                        country = stamp_el.find('country').text
                        name_of_stamp = stamp_el.find('name').text
                        year = stamp_el.find('year').text
                        series = stamp_el.find('series').text
                    
                        cursor.execute("SELECT idstamp FROM stamps WHERE idstamp = %s", (idstamp,))
                        if cursor.fetchone():
                            cursor.execute("""UPDATE stamps SET country = %s, name_of_stamp = %s, 
                                        year = %s, series = %s, idpages = %s 
                                        WHERE idstamp = %s""", 
                                     (country, name_of_stamp, year, series, idpage, idstamp))
                        else:
                            cursor.execute("""INSERT INTO stamps (idstamp, country, name_of_stamp, 
                                        year, series, idpages) 
                                        VALUES (%s, %s, %s, %s, %s, %s)""", 
                                     (idstamp, country, name_of_stamp, year, series, idpage))
        
        cnx.commit()
        cursor.close()
        cnx.close()
        
        logging.info(f"XML import completed successfully: {file_path}")
        messagebox.showinfo("Success", f"Data imported from {file_path}")
        main_screen() 
    except ValidationException as e:
        messagebox.showerror("Error", f"Cannot import from XML: {e}")

def export_to_pdf():
    try:
        logging.info("Starting PDF export")
        file_path = filedialog.asksaveasfilename(
            title="Save PDF file",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile="stamps_collection.pdf"
        )

        if not file_path:
            logging.warning("PDF export cancelled by user")
            return

        pdf_file = SimpleDocTemplate(file_path, pagesize=A4, title="Stamp collection report")
        table_data = [['Album', 'Collection', 'Page', 'Country', 'Name', 'Year', 'Series']] 
        story = []
        styles = getSampleStyleSheet()

        title = Paragraph("Stamp collection report", styles['Heading1'])
        story.append(title)
        
        albums = database_album()
        
        for album in albums:
            idalbum = album.get_idalbum()
            name_of_album = album.get_name_of_album()

            collections = database_collection(idalbum)

            for collection in collections:
                idcollection = collection.get_idcollection()
                name_of_collection = collection.get_name_of_collection()
                total_pages = collection.get_total_pages()
                pages = database_pages(idcollection)
                
                for page in pages:
                    idpage = page.get_idpage()
                    number_of_page = page.get_number_of_page()

                    stamps = database_stamp(idpage)

                    for stamp in stamps:
                        idstamp = stamp.get_idstamp()
                        country = stamp.get_country()
                        name_of_stamp = stamp.get_name_of_stamp()
                        year = stamp.get_year()
                        series = stamp.get_series()

                        table_data.append([
                            str(name_of_album),
                            str(name_of_collection),
                            str(number_of_page),
                            str(country) if country else "-",
                            str(name_of_stamp) if name_of_stamp else "-",
                            str(year) if year else "-",
                            str(series) if series else "-"
    ])

       
        stamps_table = Table(table_data, colWidths=[60, 60, 40, 70, 130, 40, 80])  
        stamps_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  
        ]))
        story.append(stamps_table)
        pdf_file.build(story)

        logging.info(f"PDF export completed successfully: {file_path}")
        messagebox.showinfo("Success", f"PDF exported to: {file_path}")

    except ValidationException as e:
        messagebox.showerror("Error", f"Error: {e}")

def main_screen():
    try:
        logging.debug("Loading main screen")
        clear_screen() 

        label_logo2 = tk.Label(content_frame, image=logo, bg='white')
        label_logo2.pack(pady=30)

        label_album2 = tk.Label(content_frame, text="Albums", bg='white')
        label_album2.pack(pady=10)

        if not albums:
            logging.warning("No albums found in database")
            no_data_label = tk.Label(content_frame, text="No albums found", bg='white', fg='red')
            no_data_label.pack(pady=20)
        else:
            for idx, album in enumerate(albums):
                idalbum = album.get_idalbum()
                name_of_album = album.get_name_of_album()

                frame = tk.Frame(content_frame, bg='white')
                frame.pack(pady=5)

                lbl = tk.Label(frame, text=name_of_album, bg='white')
                lbl.pack(side=LEFT, padx=10)

                button_choose = ttk.Button(frame, text="Сhoose", command=lambda a_id=idalbum, a_name=name_of_album, a_idx=idx: open_collection(a_id, a_name, a_idx))
                button_choose.pack(side=LEFT, padx=10)
                
        logging.info("Main screen loaded successfully")
                
    except ValidationException as main_screen_error:
        messagebox.showerror("Error", f"Cannot load main screen: {main_screen_error}")


def save_add_changes():
    try:
        logging.info("Saving changes")
        cnx = database_connection()

        if not cnx:
            messagebox.showerror("Error", "Cannot connect to database")
            return
        
        cursor = cnx.cursor()
        
        try:
            for album in albums:
                cursor.execute("SELECT idalbum FROM album WHERE idalbum = %s", (album.get_idalbum(),))
                if cursor.fetchone():
                    cursor.execute("UPDATE album SET name_of_album = %s WHERE idalbum = %s",
                                 (album.get_name_of_album(), album.get_idalbum()))
                else:
                    cursor.execute("INSERT INTO album (idalbum, name_of_album) VALUES (%s, %s)",
                                 (album.get_idalbum(), album.get_name_of_album()))
                
                for collection in album.get_collection_list():
                    cursor.execute("SELECT idcollection FROM collection WHERE idcollection = %s", 
                                 (collection.get_idcollection(),))
                    if cursor.fetchone():
                        cursor.execute("""UPDATE collection SET name_of_collection = %s, 
                                       total_pages = %s, idalbum = %s WHERE idcollection = %s""",
                                     (collection.get_name_of_collection(), collection.get_total_pages(),
                                      album.get_idalbum(), collection.get_idcollection()))
                    else:
                        cursor.execute("""INSERT INTO collection (idcollection, name_of_collection, 
                                       total_pages, idalbum) VALUES (%s, %s, %s, %s)""",
                                     (collection.get_idcollection(),collection.get_name_of_collection(),
                                      collection.get_total_pages(), album.get_idalbum()))
                    
                    for page in collection.get_pages_list():
                        cursor.execute("SELECT idpages FROM pages WHERE idpages = %s", 
                                     (page.get_idpage(),))
                        if cursor.fetchone():
                            cursor.execute("""UPDATE pages SET number_of_page = %s, 
                                           idcollection = %s WHERE idpages = %s""",
                                         (page.get_number_of_page(), collection.get_idcollection(),
                                          page.get_idpage()))
                        else:
                            cursor.execute("""INSERT INTO pages (idpages, number_of_page, idcollection) 
                                           VALUES (%s, %s, %s)""",
                                         (page.get_idpage(), page.get_number_of_page(),
                                          collection.get_idcollection()))
                            
                        for stamp in page.get_stamps_list():
                            cursor.execute("SELECT idstamp FROM stamps WHERE idstamp = %s", 
                                         (stamp.get_idstamp(),))
                            if cursor.fetchone():
                                cursor.execute("""UPDATE stamps SET country = %s, name_of_stamp = %s, 
                                               year = %s, series = %s, idpages = %s WHERE idstamp = %s""",
                                             (stamp.get_country(), stamp.get_name_of_stamp(),
                                              stamp.get_year(), stamp.get_series(),
                                              page.get_idpage(), stamp.get_idstamp()))
                            else:
                                cursor.execute("""INSERT INTO stamps (idstamp, country, name_of_stamp, 
                                               year, series, idpages) VALUES (%s, %s, %s, %s, %s, %s)""",
                                             (stamp.get_idstamp(), stamp.get_country(),
                                              stamp.get_name_of_stamp(), stamp.get_year(),
                                              stamp.get_series(), page.get_idpage()))

            cnx.commit()
            
            logging.info("Changes saved successfully")
            messagebox.showinfo("Success", "All changes have been saved")
            
        except ValidationException as save_error:
            cnx.rollback()
            logging.error(f"Error saving changes: {save_error}")
            messagebox.showerror("Save Error", f"Cannot save changes: {save_error}")
            
        finally:
            cursor.close()
            cnx.close()
            
    except ValidationException as e:
        logging.error(f"Error in save_changes function: {e}")
        messagebox.showerror("Error", f"Cannot save changes: {e}")

def save_delete_changes(album_id=None, collection_id=None, page_id=None, stamp_id=None):
    cnx = database_connection()
    cursor = cnx.cursor()
    
    try:
        queries = []
        params = []
        
        if stamp_id:
            queries.append("DELETE FROM stamps WHERE idstamp = %s")
            params.append(stamp_id)
        
        if page_id:
            queries.append("DELETE FROM pages WHERE idpages = %s")
            params.append(page_id)
        
        if collection_id:
            queries.append("DELETE FROM collection WHERE idcollection = %s")
            params.append(collection_id)
        
        if album_id:
            queries.append("DELETE FROM album WHERE idalbum = %s")
            params.append(album_id)
        
        if not queries:
            logging.warning("No IDs provided for deletion")
            return
    
        for query, param in zip(queries, params):
            cursor.execute(query, (param,))
        
        cnx.commit()
        
        logging.info("Changes saved successfully")
        messagebox.showinfo("Success", "All changes have been saved")
        
    except ValidationException as save_error:
        cnx.rollback()
        logging.error(f"Error saving changes: {save_error}")
        messagebox.showerror("Save Error", f"Cannot save changes: {save_error}")
        
    finally:
        cursor.close()
        cnx.close()
        


def add_id(table_name, column_id):
    try:
        cnx = database_connection()
        if not cnx:
            return 
        
        cursor = cnx.cursor()
        cursor.execute(f"SELECT MAX({column_id}) FROM {table_name}")
        result = cursor.fetchone()
        
        if result and result[0]:
            new_id = result[0] + 1
        else:
            new_id = 1
            
        cursor.close()
        cnx.close()
        return new_id
        
    except ValidationException as e:
        logging.error(f"Error generating ID: {e}")


def add_album():
    w_alb = Toplevel(root)
    w_alb.title("Add album")
    w_alb.geometry("350x200")
    w_alb.grab_set()
    center_child(w_alb, root)
    
    ttk.Label(w_alb, text="Enter new album name:", font=("Arial", 10, "bold")).pack(pady=(20, 10))
    album_entry = ttk.Entry(w_alb, width=30)
    album_entry.pack(pady=10)

    def new_album():
        try:
            album_name = album_entry.get().strip()
            
            ValidateTextException("Album name").check(
                album_name, 
                min_len=2, 
                max_len=50,
                existing_names=[album.get_name_of_album() for album in albums] 
            )
            new_idalbum = add_id('album', 'idalbum')
            if not new_idalbum:
                raise ValidationException("Album ID", "cannot generate ID")
            
            ValidateIntException("Album ID").check(str(new_idalbum), min_val=1)
            
            new_album = Album(new_idalbum, album_name)
            albums.append(new_album)
            save_add_changes()
            w_alb.destroy()
            messagebox.showinfo("Success", f"'{album_name}' added successfully!")
            main_screen()  
            
            logging.info(f"Album added: {album_name} (ID: {new_idalbum})")
            
        except ValidationException as e:
            logging.error(f"Error adding album: {e}")
            messagebox.showerror("Error", f"Cannot add album: {e}")
    ttk.Button(w_alb, text="Add album", command=new_album).pack(pady=20)


def add_collection():
    w_col = Toplevel(root)
    w_col.title("Add collection")
    w_col.geometry("400x300")
    w_col.grab_set()
    center_child(w_col, root)
    
    ttk.Label(w_col, text="Enter new collection name:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    collection_entry = ttk.Entry(w_col, width=30)
    collection_entry.pack(pady=5)
    
    ttk.Label(w_col, text="Number of pages:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    pages_entry = ttk.Entry(w_col, width=30)
    pages_entry.pack(pady=5)
    
    ttk.Label(w_col, text="Select album:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    album_names = [album.get_name_of_album() for album in albums]
    album_var = tk.StringVar()
    album_combo = ttk.Combobox(
        w_col,
        textvariable=album_var,
        values=album_names,
        state="readonly",
        width=28
    )
    album_combo.pack(pady=5)
    
    def new_collection():
        try:
            collection_name = collection_entry.get().strip()
            pages_text = pages_entry.get().strip()
            selected_album_name = album_var.get()
        
            ValidateTextException("Collection name").check(
                collection_name,
                min_len=2,
                max_len=50,
                existing_names=[col.get_name_of_collection() for album in albums 
                               for col in album.get_collection_list()]
            )
    
            total_pages = ValidateIntException("Number of pages").check(
                pages_text,
                min_val=1,
                max_val=3
            )
        
            if not selected_album_name:
                raise ValidationException("Album", "must select an album")
            
            selected_album = None
            for album in albums:
                if album.get_name_of_album() == selected_album_name:
                    selected_album = album
                    break
            
            if not selected_album:
                raise ValidationException("Album", "not found")
            
            new_idcollection = add_id('collection', 'idcollection')
            if not new_idcollection:
                raise ValidationException("Collection ID", "cannot generate ID")
        
            new_collection = Collection(new_idcollection, collection_name, total_pages)
            selected_album.set_collection_list(new_collection)
            save_add_changes()
            w_col.destroy()
            messagebox.showinfo("Success", f"Collection '{collection_name}' added successfully!")
            
            logging.info(f"Collection added: {collection_name} (ID: {new_idcollection}) to album: {selected_album_name}")
            
        except ValidationException as e:
            logging.error(f"Error adding collection: {e}")
            messagebox.showerror("Error", f"Cannot add collection: {e}")
    
    ttk.Button(w_col, text="Add Collection", command=new_collection).pack(pady=20)
    if album_names:
        album_combo.set(album_names[0])

def add_page():    
    all_collections = []
    for album in albums:
        for collection in album.get_collection_list():
            all_collections.append({
                'display': f"{album.get_name_of_album()} - {collection.get_name_of_collection()}",
                'album': album,
                'collection': collection
            })
    
    if not all_collections:
        messagebox.showinfo("Info", "No collections found! Please create a collection first.")
        return
    
    all_page_numbers = []
    for album in albums:
        for collection in album.get_collection_list():
            for page in collection.get_pages_list():
                all_page_numbers.append(page.get_number_of_page())
    
    w_p = Toplevel(root)
    w_p.title("Add page")
    w_p.geometry("400x250") 
    w_p.grab_set()
    center_child(w_p, root)
    
    ttk.Label(w_p, text="Enter page number:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    page_entry = ttk.Entry(w_p, width=30)
    page_entry.pack(pady=5)
    
    ttk.Label(w_p, text="Select collection:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    
    collection_display = [col['display'] for col in all_collections]
    collection_var = tk.StringVar()
    collection_combo = ttk.Combobox(
        w_p,
        textvariable=collection_var,
        values=collection_display,
        state="readonly",
        width=28
    )
    collection_combo.pack(pady=5)
    
    def new_page():
        try:
            page_number_text = page_entry.get().strip()
            selected_display = collection_var.get()
            
            if not selected_display:
                raise ValidationException("Collection", "must select a collection")
        
            selected = None
            for col in all_collections:
                if col['display'] == selected_display:
                    selected = col
                    break
            
            page_number = ValidateIntException("Page number").check(
                page_number_text,
                min_val=1,
                max_val=1000
            )

            local_numbers = []
            if selected:
                pages = selected['collection'].get_pages_list()
                local_numbers = [page.get_number_of_page() for page in pages]
            

            page_number = ValidatePageNumberException("Page number").check(
                page_number_text,
                existing_numbers=local_numbers,
                check_order=True 
            )
            
            new_idpage = add_id('pages', 'idpages')
            new_page = Pages(new_idpage, page_number)
            selected['collection'].set_pages_list(new_page)
            save_add_changes()
            w_p.destroy()
            messagebox.showinfo("Success", f"Page {page_number} added to '{selected['collection'].get_name_of_collection()}'!")
            
            logging.info(f"Page added: {page_number} (ID: {new_idpage})")
            
        except ValidationException as e:
            logging.error(f"Error adding page: {e}")
            messagebox.showerror("Error", f"Cannot add page: {e}")
    
    ttk.Button(w_p, text="Add Page", command=new_page).pack(pady=20)
    if collection_display:
        collection_combo.set(collection_display[0])


def add_stamp():
    all_pages = []
    for album in albums:
        for collection in album.get_collection_list():
            for page in collection.get_pages_list():
                all_pages.append({
                    'display': f"{album.get_name_of_album()} - {collection.get_name_of_collection()} - page {page.get_number_of_page()}",
                    'page': page
                })
    
    if not all_pages:
        messagebox.showinfo("Info", "No pages found! Please create a page first.")
        return
    
    w_stamp = Toplevel(root)
    w_stamp.title("Add stamp")
    w_stamp.geometry("450x400")
    w_stamp.grab_set()
    center_child(w_stamp, root)
    
    ttk.Label(w_stamp, text="Select page:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    page_display = [page['display'] for page in all_pages]
    page_var = tk.StringVar()
    page_combo = ttk.Combobox(
        w_stamp,
        textvariable=page_var,
        values=page_display,
        state="readonly",
        width=40
    )
    page_combo.pack(pady=5)
    
    ttk.Label(w_stamp, text="Country:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    country_entry = ttk.Entry(w_stamp, width=35)
    country_entry.pack(pady=5)
    
    ttk.Label(w_stamp, text="Stamp name:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    name_entry = ttk.Entry(w_stamp, width=35)
    name_entry.pack(pady=5)
    
    ttk.Label(w_stamp, text="Year:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    year_entry = ttk.Entry(w_stamp, width=35)
    year_entry.pack(pady=5)
    
    ttk.Label(w_stamp, text="Series:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    series_entry = ttk.Entry(w_stamp, width=35)
    series_entry.pack(pady=5)
    
    def add_new_stamp():
        try:
            selected_display = page_var.get()
            country = country_entry.get().strip()
            name = name_entry.get().strip()
            year_text = year_entry.get().strip()
            series = series_entry.get().strip()
        
            if not selected_display:
                raise ValidationException("Page", "must select a page")
            selected_page = None
            for page_data in all_pages:
                if page_data['display'] == selected_display:
                    selected_page = page_data['page']
                    break
            
            if not selected_page:
                raise ValidationException("Page", "not found")
        
            ValidateTextException("Country").check(
                country,
                min_len=2,
                max_len=50
            )
            
            ValidateTextException("Stamp name").check(
                name,
                min_len=2,
                max_len=100
            )
        
            year = ValidateIntException("Year").check(
                year_text,
                min_val=1840,  
                max_val=2025   
            )
            
            ValidateTextException("Series").check(
                series,
                min_len=2,
                max_len=50
            )
            
            new_idstamp = add_id("stamps", "idstamp")
            if not new_idstamp:
                raise ValidationException("Stamp ID", "cannot generate ID")
            
            new_stamp = Stamps(new_idstamp, name, country, year, series)
            selected_page.set_stamps_list(new_stamp)
            save_add_changes()
            w_stamp.destroy()
            messagebox.showinfo("Success", f"Stamp '{name}' added successfully!")
            
            logging.info(f"Stamp added: {name} (ID: {new_idstamp}), Country: {country}, Year: {year}, Series: {series}")
            
        except ValidationException as e:
            logging.error(f"Error adding stamp: {e}")
            messagebox.showerror("Error", f"Cannot add stamp: {e}")
    
    ttk.Button(w_stamp, text="Add stamp", command=add_new_stamp).pack(pady=15)
    if page_display:
        page_combo.set(page_display[0])


def center_child(win, parent):
    parent.update_idletasks()
    win.update_idletasks()

    x = parent.winfo_x() + (parent.winfo_width() // 2) - (win.winfo_width() // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (win.winfo_height() // 2)

    win.geometry(f"+{x}+{y}")

def delete_param():
    w_del = Toplevel(root)
    w_del.title("Delete")
    w_del.geometry("350x200")
    w_del.grab_set()
    center_child(w_del, root)

    ttk.Label(w_del, text="Choose type:").pack(pady=(10, 5))
    types = ["Album", "Collection", "Page", "Stamp"]
    type_var = tk.StringVar(value=types[0])
    ttk.Combobox(w_del, textvariable=type_var, values=types, state="readonly", width=25).pack(pady=5)

    ttk.Label(w_del, text="Select item:").pack(pady=(10, 5))

    def update_items(*args):
        item_type = type_var.get()
        items = []
        
        if item_type == "Album":
            for album in albums:
                items.append(f"{album.get_idalbum()}: {album.get_name_of_album()}")
            
        elif item_type == "Collection":
            for album in albums:
                for collection in album.get_collection_list():
                    items.append(f"{collection.get_idcollection()}: {collection.get_name_of_collection()} ({album.get_name_of_album()})")
                    
        elif item_type == "Page":
            for album in albums:
                for collection in album.get_collection_list():
                    for page in collection.get_pages_list():
                        items.append(f"{page.get_idpage()}: Page {page.get_number_of_page()} ({album.get_name_of_album()} - {collection.get_name_of_collection()})")
                        
        elif item_type == "Stamp":
            for album in albums:
                for collection in album.get_collection_list():
                    for page in collection.get_pages_list():
                        for stamp in page.get_stamps_list():
                            items.append(f"{stamp.get_idstamp()}: {stamp.get_name_of_stamp()} ({album.get_name_of_album()} - {collection.get_name_of_collection()} - Page {page.get_number_of_page()})")
    
        items.sort(key=lambda x: int(x.split(':')[0]))
        item_combo['values'] = items
        if items:
            item_combo.set(items[0])
        else:
            item_combo.set('')
    
    item_var = tk.StringVar()
    item_combo = ttk.Combobox(w_del, textvariable=item_var, values=[], state="readonly", width=40)
    item_combo.pack(pady=5)
    
    type_var.trace('w', update_items)
    update_items()  

    def delete_action():
        item_type = type_var.get()
        item_text = item_var.get()

        try:
            if not item_text:
                raise ValidationException(f"{item_type}", "must select an item")
    
            item_id_str = item_text.split(':')[0].strip()
            item_id = ValidateIntException(f"{item_type} ID").check(item_id_str, min_val=1)

            if item_type == "Album":
                album_found = False
                for a in albums:
                    if a.get_idalbum() == item_id:
                        save_delete_changes(album_id=item_id)
                        albums.remove(a)
                        messagebox.showinfo("Success", "Album deleted!")
                        w_del.destroy()
                        main_screen()
                        album_found = True
                        break
                
                if not album_found:
                    raise ValidationException("Album", "not found")

            elif item_type == "Collection":
                collection_found = False
                for a in albums:
                    if a.remove_collection(item_id):
                        save_delete_changes(collection_id=item_id)
                        messagebox.showinfo("Success", "Collection deleted!")
                        w_del.destroy()
                        collection_found = True
                        break
                
                if not collection_found:
                    raise ValidationException("Collection", "not found")

            elif item_type == "Page":
                page_found = False
                for a in albums:
                    for c in a.get_collection_list():
                        if c.remove_page(item_id):
                            save_delete_changes(page_id=item_id)
                            messagebox.showinfo("Success", "Page deleted!")
                            w_del.destroy()
                            page_found = True
                            break
                    if page_found:
                        break
                
                if not page_found:
                    raise ValidationException("Page", "not found")

            elif item_type == "Stamp":
                stamp_found = False
                for a in albums:
                    for c in a.get_collection_list():
                        for p in c.get_pages_list():
                            if p.remove_stamp(item_id):
                                save_delete_changes(stamp_id=item_id)
                                messagebox.showinfo("Success", "Stamp deleted!")
                                w_del.destroy()
                                stamp_found = True
                                break
                        if stamp_found:
                            break
                    if stamp_found:
                        break
                
                if not stamp_found:
                    raise ValidationException("Stamp", "not found")

        except ValidationException as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(w_del, text="Delete", command=delete_action).pack(pady=15)

def search_by_series():
    try:
        all_series= set()
        for album in albums:
            for collection in album.get_collection_list():
                for page in collection.get_pages_list():
                    for stamp in page.get_stamps_list():
                        series_name = stamp.get_series()
                        if series_name and series_name.strip():  
                            all_series.add(series_name.strip())  
        
        if not all_series:
            messagebox.showinfo("Info", "No series found in the database!")
            return
        
        sorted_series = sorted(all_series)
        
        w_search = Toplevel(root)
        w_search.title("Search by series")
        w_search.geometry("350x150")
        w_search.grab_set()
        center_child(w_search, root)
        ttk.Label(w_search, text="Select series:").pack(pady=(20, 5))
        
        series_var = tk.StringVar()
        series_combo = ttk.Combobox(
            w_search, 
            textvariable=series_var,
            values=sorted_series,
            state="readonly",
            width=30
        )
        series_combo.pack(pady=5)
        
        def start_search():
            try:
                series_to_search = series_var.get().strip()
                
                if not series_to_search:
                    messagebox.showwarning("Warning", "Please select series!")
                    return
                
                ValidateTextException("Series name").check(series_to_search, min_len=1, max_len=100)
                w_search.destroy()
                
                logging.info(f"Searching for series: '{series_to_search}'")
    
                results = []
                for album in albums:
                    for collection in album.get_collection_list():
                        for page in collection.get_pages_list():
                            for stamp in page.get_stamps_list():
                                if stamp.get_series() == series_to_search:
                                    results.append({
                                        'album': album.get_name_of_album(),
                                        'collection': collection.get_name_of_collection(),
                                        'page': page.get_number_of_page(),
                                        'stamp': stamp
                                    })
                
                w_results = Toplevel(root)
                w_results.title(f"Search result")
                w_results.geometry("750x500")
                center_child(w_results, root)
                
                title_text = f"Found {len(results)} stamp(s) in series: '{series_to_search}'"
                ttk.Label(w_results, text=title_text, font=("Arial", 11, "bold")).pack(pady=10)
                
                if not results:
                    ttk.Label(w_results, text="No stamps found", font=("Arial", 10), foreground="gray").pack(pady=50)
                    ttk.Button(w_results, text="Close", command=w_results.destroy).pack(pady=10)
                    return
                
                tree_frame = tk.Frame(w_results)
                tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                columns = ("Album", "Collection", "Page", "Stamp Name", "Country", "Year", "ID")
                tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
                
                column_widths = [120, 120, 60, 150, 100, 60, 50]
                
                for i in range(len(columns)):
                    col = columns[i]
                    width = column_widths[i]
                    tree.heading(col, text=col)
                    tree.column(col, width=width, anchor="center")
                
                for result in results:
                    tree.insert("", tk.END, values=(
                        result['album'],
                        result['collection'],
                        result['page'],
                        result['stamp'].get_name_of_stamp(),
                        result['stamp'].get_country(),
                        result['stamp'].get_year(),
                        result['stamp'].get_idstamp()
                    ))
                
                scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                
                logging.info(f"Search results displayed. Found {len(results)} items.")
                
            except ValidationException as e:
                logging.error(f"Error during search: {e}")
                messagebox.showerror("Search Error", f"Cannot perform search: {e}")
        
        ttk.Button(w_search, text="Search", command=start_search).pack(pady=10)
        
        if sorted_series:
            series_combo.set(sorted_series[0])
        
    except ValidationException as e:
        logging.error(f"Error in search_by_series: {e}")
        messagebox.showerror("Error", f"Cannot initialize search: {e}")
        
                
def search_by_location():
    try:
        if not albums:
            messagebox.showinfo("Info", "No albums found in the database!")
            return
        
        w_search = Toplevel(root)
        w_search.title("Search by location")
        w_search.geometry("400x250")
        w_search.grab_set()
        center_child(w_search, root)
        ttk.Label(w_search, text="Select location:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
        
        ttk.Label(w_search, text="Album:").pack(pady=(5, 2))
        album_names = [album.get_name_of_album() for album in albums]
        album_var = tk.StringVar()
        album_combo = ttk.Combobox(
            w_search, 
            textvariable=album_var,
            values=album_names,
            state="readonly",
            width=30
        )
        album_combo.pack(pady=2)
        
       
        ttk.Label(w_search, text="Collection:").pack(pady=(10, 2)) 
        collection_var = tk.StringVar()
        collection_combo = ttk.Combobox(
            w_search, 
            textvariable=collection_var,
            values=[],  
            state="readonly",
            width=30
        )
        collection_combo.pack(pady=2)
        
        
        ttk.Label(w_search, text="Page number:").pack(pady=(10, 2))
        page_var = tk.StringVar()
        page_combo = ttk.Combobox(
            w_search, 
            textvariable=page_var,
            values=[], 
            state="readonly",
            width=30
        )
        page_combo.pack(pady=2)
        
        def update_collections(event=None):
            selected_album_name = album_var.get()
            if not selected_album_name:
                return
            selected_album = None
            for album in albums:
                if album.get_name_of_album() == selected_album_name:
                    selected_album = album
                    break
            
            if selected_album:
                collections = selected_album.get_collection_list()
                collection_names = [col.get_name_of_collection() for col in collections]
                collection_combo['values'] = collection_names
                collection_var.set('') 
                page_combo['values'] = []  
                page_var.set('')
                if collection_names:
                    collection_combo.set(collection_names[0])
    
        def update_pages(event=None):
            selected_album_name = album_var.get()
            selected_collection_name = collection_var.get()
            
            if not selected_album_name or not selected_collection_name:
                return
            
            selected_collection = None
            for album in albums:
                if album.get_name_of_album() == selected_album_name:
                    for collection in album.get_collection_list():
                        if collection.get_name_of_collection() == selected_collection_name:
                            selected_collection = collection
                            break
                    break
            
            if selected_collection:
                pages = selected_collection.get_pages_list()
                page_numbers = sorted([page.get_number_of_page() for page in pages])
                page_combo['values'] = page_numbers
                page_var.set('')
                
                if page_numbers:
                    page_combo.set(str(page_numbers[0]))
        
        album_combo.bind("<<ComboboxSelected>>", update_collections)
        collection_combo.bind("<<ComboboxSelected>>", update_pages)
        
        def start_searchl():
            try:
                album_name = album_var.get().strip()
                collection_name = collection_var.get().strip()
                page_number_str = page_var.get().strip()
                
                if not album_name:
                    messagebox.showwarning("Warning", "Please select album!")
                    return
                if not collection_name:
                    messagebox.showwarning("Warning", "Please select collection!")
                    return
                if not page_number_str:
                    messagebox.showwarning("Warning", "Please select page!")
                    return
                
                ValidateTextException("Album name").check(album_name, min_len=1)
                ValidateTextException("Collection name").check(collection_name, min_len=1)
                page_number = ValidateIntException("Page number").check(page_number_str, min_val=1)
                
                w_search.destroy()
                
                logging.info(f"Searching at location: {album_name} > {collection_name} > Page {page_number}")
                
                found_stamps = []
                
                for album in albums:
                    if album.get_name_of_album() == album_name:
                        for collection in album.get_collection_list():
                            if collection.get_name_of_collection() == collection_name:
                                for page in collection.get_pages_list():
                                    if page.get_number_of_page() == page_number:
                                        found_stamps = page.get_stamps_list()
                                        break
                                break
                        break
                
                w_results = Toplevel(root)
                w_results.title(f"Search results")
                w_results.geometry("750x500")
                center_child(w_results, root)
                
                location_text = f"Location: {album_name} - {collection_name} - Page {page_number}"
                ttk.Label(w_results, text=location_text, font=("Arial", 11, "bold")).pack(pady=(10, 5))
                
                title_text = f"Found {len(found_stamps)} stamp(s) at this location"
                ttk.Label(w_results, text=title_text, font=("Arial", 10)).pack(pady=(0, 10))
                
                if not found_stamps:
                    ttk.Label(w_results, text="No stamps found at this location", 
                             font=("Arial", 10), foreground="gray").pack(pady=50)
                    ttk.Button(w_results, text="Close", command=w_results.destroy).pack(pady=10)
                    return
                
                tree_frame = tk.Frame(w_results)
                tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
                
                columns = ("ID", "Stamp Name", "Country", "Series", "Year")
                tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
                
                column_widths = [50, 200, 100, 150, 60]
                
                for i in range(len(columns)):
                    col = columns[i]
                    width = column_widths[i]
                    tree.heading(col, text=col)
                    tree.column(col, width=width, anchor="center")
                
                for stamp in found_stamps:
                    tree.insert("", tk.END, values=(
                        stamp.get_idstamp(),
                        stamp.get_name_of_stamp(),
                        stamp.get_country(),
                        stamp.get_series(),
                        stamp.get_year()
                    ))
                
                scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
                tree.configure(yscroll=scrollbar.set)
                tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                        
                logging.info(f"Location search results displayed. Found {len(found_stamps)} stamps.")
                
            except ValidationException as e:
                logging.error(f"Error during location search: {e}")
                messagebox.showerror("Search Error", f"Cannot perform search: {e}")
        
        ttk.Button(w_search, text="Search", command=start_searchl).pack(pady=15)

        if album_names:
            album_combo.set(album_names[0])
            update_collections()
        
    except ValidationException as e:
        logging.error(f"Error in search_by_location: {e}")
        messagebox.showerror("Error", f"Cannot initialize search: {e}")


def show_countries():
    w_coun = Toplevel(root)
    w_coun.title("Countries in collections")
    w_coun.geometry("500x400")
    center_child(w_coun, root)

    try:
        if not albums:
            no_data_label = ttk.Label(w_coun, text="No albums found.", font=("Arial", 10))
            no_data_label.pack(pady=50)
            ttk.Button(w_coun, text="Close", command=w_coun.destroy).pack(pady=10)
            return
        
        canvas = tk.Canvas(w_coun)
        scrollbar = ttk.Scrollbar(w_coun, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        for album in albums:
            album_label = ttk.Label(scrollable_frame, text=f"Album: {album.get_name_of_album()}", font=('Helvetica', 12, "bold"))
            album_label.pack(pady=(10, 5), anchor=tk.W, padx=10)
            
            for collection in album.get_collection_list():
                countries_list = []
                for page in collection.get_pages_list():
                    for stamp in page.get_stamps_list():
                        country = stamp.get_country()
                        if country and country not in countries_list:
                            countries_list.append(country)
                
                countries_list.sort()
                
                if countries_list:
                    coll_label = ttk.Label(scrollable_frame, text=f"  Collection: {collection.get_name_of_collection()}", font=('Helvetica', 12))
                    coll_label.pack(pady=(5, 2), anchor=tk.W, padx=20)
                    
                    for country in countries_list:
                        country_label = ttk.Label(scrollable_frame, text=f"-{country}")
                        country_label.pack(anchor=tk.W, padx=30)
    
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    except ValidationException as e:
        messagebox.showerror("Error", f"Cannot open info: {e}")


def edit_album():
    w_alb = Toplevel(root)
    w_alb.title("Edit album")
    w_alb.geometry("350x250")
    w_alb.grab_set()
    center_child(w_alb, root)

    album_items = []
    for album in albums:
        album_items.append(f"{album.get_idalbum()}: {album.get_name_of_album()}")

    ttk.Label(w_alb, text="Select album:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    
    album_var = tk.StringVar()
    album_combo = ttk.Combobox(
        w_alb,
        textvariable=album_var,
        values=album_items,
        state="readonly",
        width=30
    )
    album_combo.pack(pady=5)

    ttk.Label(w_alb, text="New name:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    name_entry = ttk.Entry(w_alb, width=30)
    name_entry.pack(pady=5)
    
    def edit_alb():
        try:
            selected_text = album_var.get()
            
            if not selected_text:
                raise ValidationException("Album", "must select an album")
            
            album_id_str = selected_text.split(':')[0].strip()
            album_id = ValidateIntException("Album ID").check(album_id_str, min_val=1)
            
            new_name = ValidateTextException("Album name").check(
                name_entry.get().strip(), 
                min_len=2,
                max_len=50,
                existing_names=[a.get_name_of_album() for a in albums if a.get_idalbum() != album_id]
            )

            for album in albums:
                if album.get_idalbum() == album_id:
                    album.set_name_of_album(new_name)
                    save_add_changes()
                    messagebox.showinfo("Success", "Album updated!")
                    w_alb.destroy()
                    main_screen()
                    logging.info(f"Album updated: ID {album_id}, new name: {new_name}")
                    return

            raise ValidationException("Album", "not found")

        except ValidationException as e:
            messagebox.showerror("Validation error", str(e))

    ttk.Button(w_alb, text="Edit", command=edit_alb).pack(pady=15)
    if album_items:
        album_combo.set(album_items[0])


def edit_collection():
    w_col = Toplevel(root)
    w_col.title("Edit collection")
    w_col.geometry("350x280")
    w_col.grab_set()
    center_child(w_col, root)
    
    collection_items = []
    for album in albums:
        for collection in album.get_collection_list():
            collection_items.append(f"{collection.get_idcollection()}: {collection.get_name_of_collection()} ({album.get_name_of_album()})")

    ttk.Label(w_col, text="Select collection:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    
    collection_var = tk.StringVar()
    collection_combo = ttk.Combobox(
        w_col,
        textvariable=collection_var,
        values=collection_items,
        state="readonly",
        width=35
    )
    collection_combo.pack(pady=5)

    ttk.Label(w_col, text="New name:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    name_entry = ttk.Entry(w_col, width=35)
    name_entry.pack(pady=5)

    ttk.Label(w_col, text="New total pages:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    pages_entry = ttk.Entry(w_col, width=35)
    pages_entry.pack(pady=5)

    def edit_col():
        try:
            selected_text = collection_var.get()
            
            if not selected_text:
                raise ValidationException("Collection", "must select a collection")
            
            col_id_str = selected_text.split(':')[0].strip()
            col_id = ValidateIntException("Collection ID").check(col_id_str, min_val=1)
            
            new_name = ValidateTextException("Collection name").check(
                name_entry.get().strip(),
                min_len=2,
                max_len=50
            )
            
            new_pages = ValidateIntException("Total pages").check(
                pages_entry.get().strip(),
                min_val=1,
                max_val=1000
            )

            collection_found = False
            for alb in albums:
                for col in alb.get_collection_list():
                    if col.get_idcollection() == col_id:
                        col.set_name_of_collection(new_name)
                        col.set_total_pages(new_pages)
                        save_add_changes()
                        messagebox.showinfo("Success", "Collection updated!")
                        w_col.destroy()
                        collection_found = True
                        return
            
            if not collection_found:
                raise ValidationException("Collection", "not found")

        except ValidationException as e:
            messagebox.showerror("Validation error", str(e))

    ttk.Button(w_col, text="Edit", command=edit_col).pack(pady=15)
    
    if collection_items:
        collection_combo.set(collection_items[0])
      
def edit_stamp():
    w_stamp = Toplevel(root)
    w_stamp.title("Edit stamp")
    w_stamp.grab_set()
    w_stamp.geometry("400x400")

    center_child(w_stamp, root)

    stamp_items = []
    for album in albums:
        for collection in album.get_collection_list():
            for page in collection.get_pages_list():
                for stamp in page.get_stamps_list():
                    stamp_items.append(f"{stamp.get_idstamp()}: {stamp.get_name_of_stamp()} ({album.get_name_of_album()} - {collection.get_name_of_collection()} - page {page.get_number_of_page()})")

    ttk.Label(w_stamp, text="Select stamp:", font=("Arial", 10, "bold")).pack(pady=(10, 5))
    
    stamp_var = tk.StringVar()
    stamp_combo = ttk.Combobox(
        w_stamp,
        textvariable=stamp_var,
        values=stamp_items,
        state="readonly",
        width=50
    )
    stamp_combo.pack(pady=5)

    ttk.Label(w_stamp, text="Country:").pack(pady=(10, 3))
    country_entry = ttk.Entry(w_stamp, width=40)
    country_entry.pack(pady=3)

    ttk.Label(w_stamp, text="Name:").pack(pady=(5, 3))
    name_entry = ttk.Entry(w_stamp, width=40)
    name_entry.pack(pady=3)

    ttk.Label(w_stamp, text="Year:").pack(pady=(5, 3))
    year_entry = ttk.Entry(w_stamp, width=40)
    year_entry.pack(pady=3)

    ttk.Label(w_stamp, text="Series:").pack(pady=(5, 3))
    series_entry = ttk.Entry(w_stamp, width=40)
    series_entry.pack(pady=3)

    def edit_st():
        try:
            selected_text = stamp_var.get()
            
            if not selected_text:
                raise ValidationException("Stamp", "must select a stamp")
            
            stamp_id_str = selected_text.split(':')[0].strip()
            stamp_id = ValidateIntException("Stamp ID").check(stamp_id_str, min_val=1)
            
            new_country = ValidateTextException("Country").check(
                country_entry.get().strip(),
                min_len=2,
                max_len=50
            )
            
            new_name = ValidateTextException("Stamp name").check(
                name_entry.get().strip(),
                min_len=2,
                max_len=100
            )
            
            new_year = ValidateIntException("Year").check(
                year_entry.get().strip(),
                min_val=1700,
                max_val=2025
            )
            
            new_series = ValidateTextException("Series").check(
                series_entry.get().strip(),
                min_len=2,
                max_len=50
            )

            stamp_found = False
            for album in albums:
                for collection in album.get_collection_list():
                    for page in collection.get_pages_list():
                        for stamp in page.get_stamps_list():
                            if stamp.get_idstamp() == stamp_id:
                                stamp.set_country(new_country)
                                stamp.set_name_of_stamp(new_name)
                                stamp.set_year(new_year)
                                stamp.set_series(new_series)
                                
                                save_add_changes()
                                messagebox.showinfo("Success", "Stamp updated!")
                                w_stamp.destroy()
                                logging.info(f"Stamp updated: ID {stamp_id}")
                                stamp_found = True
                                return
            
            if not stamp_found:
                raise ValidationException("Stamp", "not found")

        except ValidationException as e:
            messagebox.showerror("Validation error", str(e))

    ttk.Button(w_stamp, text="Edit", command=edit_st).pack(pady=15)
    if stamp_items:
        stamp_combo.set(stamp_items[0])
    
logging.info("Starting main screen")
main_screen()

root.option_add("*tearOff", FALSE)
main_menu = Menu()
file_menu = Menu()
settings_menu = Menu()
settings_two_menu = Menu()
info_menu = Menu()
edit_menu = Menu()
search_menu = Menu()

settings_menu.add_command(label="XML", command=export_to_xml)
settings_menu.add_command(label="PDF",command=export_to_pdf)

settings_two_menu.add_command(label="Album", command=add_album)
settings_two_menu.add_command(label="Collection", command=add_collection)
settings_two_menu.add_command(label="Page", command=add_page)
settings_two_menu.add_command(label="Stamp", command=add_stamp)

edit_menu.add_command(label="Album", command=edit_album)
edit_menu.add_command(label="Collection", command=edit_collection)
edit_menu.add_command(label="Stamp", command=edit_stamp)

info_menu.add_command(label="About collection", command=show_countries)
search_menu.add_command(label="By series", command=search_by_series)
search_menu.add_command(label="By location", command=search_by_location)

file_menu.add_cascade(label="Edit", menu=edit_menu)
file_menu.add_cascade(label="Save as", menu=settings_menu)
file_menu.add_command(label="Delete", command=delete_param) 
file_menu.add_cascade(label="Add", menu=settings_two_menu)
file_menu.add_command(label="Import", command=import_from_xml)
file_menu.add_command(label="Exit")
main_menu.add_cascade(label="File", menu=file_menu)
root.config(menu=main_menu)

main_menu.add_cascade(label="Search", menu=search_menu)
main_menu.add_cascade(label="Info", menu=info_menu)

root.mainloop()
logging.info("Application closed")

