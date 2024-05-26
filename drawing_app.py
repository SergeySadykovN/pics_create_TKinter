import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw


class DrawingApp:
    def __init__(self, root):
        '''инициализирует основные атрибуты и настраивает элементы холста и пользовательского интерфейса.'''

        # root : корневой виджет Tkinter, который служит контейнером для всего интерфейса приложения.
        self.root = root
        self.root.title("Рисовалка с сохранением в PNG")

        # self.image : пустое изображение с заданным размером и цветом.
        self.image = Image.new("RGB", (1200, 800), "white")
        # self.draw : ImageDraw объект, используемый для рисования на изображении.
        self.draw = ImageDraw.Draw(self.image)

        # self.canvas : виджет холста Tkinter, где пользователи будут рисовать.
        self.canvas = tk.Canvas(root, width=1200, height=800, bg='white')
        self.canvas.pack()

        # вызывает метод для настройки элементов управления пользовательского интерфейса.
        self.setup_ui()

        # отслеживает последнюю позицию курсора для рисования.
        self.last_x, self.last_y = None, None

        # устанавливает цвет пера по умолчанию
        self.pen_color = 'green'

        # переменная для хранения текущего размера кисти
        self.brush_size = 1

        # переменная для хранения предыдущего цвета пера
        self.prevision_pen_color = self.pen_color

        # Стек для хранения истории действий
        self.history = []
        # Стек для хранения отменеенных действий
        self.redo_stack = []

        # привязывает событие перетаскивания левой кнопки мыши к paint методу.
        self.canvas.bind('<B1-Motion>', self.paint)
        # привязывает событие отпускания левой кнопки мыши к reset методу.
        self.canvas.bind('<ButtonRelease-1>', self.reset)
        # привязывает событие для правой кнопки мыши для выбора цвета пикселя
        self.canvas.bind('<Button-3>', self.pick_color)

        # привязка горячих клавиш
        self.root.bind('<Control-s>', self.save_image)  # сохранение изображение
        self.root.bind('<Control-c>', self.choose_color)  # выбор цвета
        self.root.bind('<Control-z>', self.undo)  # отмена последнего действия
        self.root.bind('<Control-y>', self.redo)  # повтор последненего отмененного действия
        self.root.bind('<Control-q>', self.clear_canvas)  # очистка холста
        self.root.bind('<Control-e>', self.use_eraser)  # ластик

    def setup_ui(self):
        '''Настройка пользовательского интерфейса.
         Создает и упаковывает кнопки управления и шкалу размера кисти.'''
        # tk.Frame : контейнер для хранения кнопок управления.
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X)

        # tk.Button : Кнопки для очистки холста, выбора цвета, ластика, сохранения изображения, отмены и повтора.
        clear_button = tk.Button(control_frame, text="Очистить\nCTR+Q", command=self.clear_canvas)
        clear_button.pack(side=tk.LEFT)

        color_button = tk.Button(control_frame, text="Выбрать цвет\nCTR+C", command=self.choose_color)
        color_button.pack(side=tk.LEFT)

        eraser_button = tk.Button(control_frame, text="Ластик\nCTR+E", command=self.use_eraser)
        eraser_button.pack(side=tk.LEFT)

        save_button = tk.Button(control_frame, text="Сохранить\nCTR+S", command=self.save_image)
        save_button.pack(side=tk.LEFT)

        undo_button = tk.Button(control_frame, text="Отменить\nCTR+Z", command=self.undo)
        undo_button.pack(side=tk.LEFT)

        redo_button = tk.Button(control_frame, text="Повторить\nCTR+Y", command=self.redo)
        redo_button.pack(side=tk.LEFT)

        # список размеров кисти
        sizes = [x for x in range(1, 21)]
        self.brush_size_var = tk.IntVar(value=sizes[0])

        # `tk.OptionMenu`, связанное с переменной `self.brush_size_var`, для выбора размера кисти
        brush_size_menu = tk.OptionMenu(control_frame, self.brush_size_var, *sizes, command=self.update_brush_size)
        brush_size_menu.pack(side=tk.LEFT)

    def update_brush_size(self, value):
        '''Обновляет значение `self.brush_size`
        при выборе нового размера из выпадающего меню'''
        self.brush_size = int(value)

    def paint(self, event):
        '''Метод рисования : рисует линии на холсте и изображении при перетаскивании мыши'''
        if self.last_x and self.last_y:
            # create_line : рисует линию на холсте от последней записанной позиции до текущей позиции.
            self.canvas.create_line(self.last_x, self.last_y, event.x, event.y,
                                    width=self.brush_size, fill=self.pen_color,
                                    capstyle=tk.ROUND, smooth=tk.TRUE)
            # draw.line : рисует линию на изображении PIL для последующего сохранения
            self.draw.line([self.last_x, self.last_y, event.x, event.y], fill=self.pen_color,
                           width=self.brush_size)

            # сохраняем дейсвие в истории
            self.history.append(('line', (self.last_x, self.last_y, event.x, event.y), self.pen_color, self.brush_size))
            # очистка стека отмен после нового действия
            self.redo_stack.clear()

        self.last_x = event.x
        self.last_y = event.y

    def reset(self, event):
        '''сбрасывает последнюю позицию курсора при отпускании кнопки мыши'''
        self.last_x, self.last_y = None, None

    def clear_canvas(self, event=None):
        '''очищает холст и сбрасывает изображение до пустого белого изображения'''
        self.canvas.delete("all")
        self.image = Image.new("RGB", (600, 400), "white")
        self.draw = ImageDraw.Draw(self.image)

    def choose_color(self, event=None):
        '''открывает диалоговое окно выбора цвета для выбора цвета пера.'''
        # Обновляет `self.previous_pen_color` перед выбором нового цвета.
        self.prevision_pen_color = self.pen_color
        self.pen_color = colorchooser.askcolor(color=self.pen_color)[1]

    def use_eraser(self, event=None):
        '''Устанавливает `self.pen_color` в "white" для использования ластика.'''
        self.pen_color = 'white'

    def pick_color(self, event):
        '''Привязан к событию `<Button-3>` (правая кнопка мыши) на холсте.'''
        x, y = event.x, event.y
        # #%02x%02x%02x : шестнадцатеричный цветовой код -> hex строка вида #RRGGBB
        self.pen_color = '#%02x%02x%02x' % self.image.getpixel((x, y))

    def save_image(self, event=None):
        '''открывает диалоговое окно для сохранения изображения в формате PNG.'''
        file_path = filedialog.asksaveasfilename(filetypes=[('PNG files', '*.png')])
        if file_path:
            if not file_path.endswith('.png'):
                file_path += '.png'
            self.image.save(file_path)
            messagebox.showinfo("Информация", "Изображение успешно сохранено!")

    def undo(self, event=None):
        '''Отменяет последнее действие'''
        if self.history:
            last_action = self.history.pop()
            self.redo_stack.append(last_action)
            self.redraw_from_history()

    def redo(self, event=None):
        '''Повторяет последнее отмененное действие'''
        if self.redo_stack:
            last_undone_action = self.redo_stack.pop()
            self.history.append(last_undone_action)
            self.redraw_from_history()

    def redraw_from_history(self):
        '''Перерисовывает все действия из истории'''
        self.clear_canvas()
        for action in self.history:
            if action[0] == 'line':
                _, coords, color, width = action
                self.canvas.create_line(coords, width=width, fill=color, capstyle=tk.ROUND, smooth=tk.TRUE)
                self.draw.line(coords, fill=color, width=width)


def main():
    '''Основная функция : Создает главное окно приложения и
    запускает цикл событий Tkinter.'''
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
