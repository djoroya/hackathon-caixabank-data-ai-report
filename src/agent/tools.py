from fpdf import FPDF
import os
from fpdf.enums import XPos, YPos


folder_file = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(folder_file, "..", "..", "reports", "figures")
report_path = os.path.join(folder_file, "..", "..", "reports")
# Función para crear un PDF con una lista de tablas e imágenes en el orden dado
def crear_pdf_elementos(rfs, res, ree, nombre_pdf):
    img1 = os.path.join(img_path, "earnings_and_expenses.png")
    img2 = os.path.join(img_path, "expenses_summary.png")

    # Lista de elementos (tablas e imágenes) en el orden deseado
    elementos = [
        {"tipo": "tabla", "data": rfs, "titulo": "Cash Flow Summary", "col_width": 30, "x0": 30},
        {"tipo": "tabla", "data": res, "titulo": "Expenses Summary", "col_width": 30, "x0": 20},
        {"tipo": "tabla", "data": ree, "titulo": "Earnings and Expenses", "col_width": 30, "x0": 80},
        {"tipo": "imagen", "path": img1, "col_width": 30},
        {"tipo": "imagen", "path": img2, "col_width": 30},
    ]

    pdf = FPDF()
    pdf.add_page()  # Solo se agrega una página al inicio
    pdf.set_auto_page_break(auto=False)  # Desactivar salto automático de página
    pdf.set_font("helvetica", size=10)

    # Margen superior y espacio entre elementos
    top_margin = 10
    espacio_entre_elementos = 15
    page_height = pdf.h - 15  # Altura de la página con margen inferior
    row_height = pdf.font_size * 1.5  # Altura de fila para las tablas

    # Posición vertical inicial
    y_position = top_margin

    for elemento in elementos:
        col_width = elemento["col_width"]
        # Control de salto de página si no hay espacio suficiente
        if elemento["tipo"] == "tabla":
            num_rows = len(elemento["data"]) + 2  # filas + encabezados + título
            table_height = num_rows * row_height + espacio_entre_elementos
            if y_position + table_height > page_height:
                pdf.add_page()
                y_position = top_margin

            # Imprimir título de la tabla
            x0 = elemento["x0"]
            pdf.set_xy(20, y_position)
            pdf.set_font("helvetica", "B", 12)
            # pdf.cell(0, 10, elemento["titulo"], ln=True, align="C")
            pdf.cell(0, 10, elemento["titulo"], align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


            y_position += 10  # Mover después del título

            # Encabezados de la tabla
            pdf.set_font("helvetica", "B", 10)
            pdf.set_xy(x0, y_position)
            for column in elemento["data"].columns:
                nlen = 10
                column = column[:nlen] + "..." if len(column) > nlen else column
                pdf.cell(col_width, row_height, column, border=1, align="C")
            y_position += row_height

            # Filas de la tabla
            pdf.set_font("helvetica", "", 10)
            for _, row in elemento["data"].iterrows():
                pdf.set_xy(x0, y_position)
                for item in row:
                    item = str(item)
                    item = item[:10] + "..." if len(item) > 10 else item
                    pdf.cell(col_width, row_height, item, border=1, align="C")
                y_position += row_height

        elif elemento["tipo"] == "imagen":
            # Altura de la imagen (ajústala si es necesario)
            image_height = 50 + espacio_entre_elementos
            if y_position + image_height > page_height:
                pdf.add_page()
                y_position = top_margin

            # Agregar imagen
            pdf.set_xy(20, y_position)
            pdf.image(elemento["path"], x=60, y=y_position, w=80)  # Ajusta el ancho según el tamaño deseado
            y_position += image_height

        # Espacio entre elementos
        y_position += espacio_entre_elementos

    # Guardar el PDF
    nombre_pdf = os.path.join(report_path, nombre_pdf)

    if os.path.exists(nombre_pdf):
        os.remove(nombre_pdf)

    pdf.output(nombre_pdf)

