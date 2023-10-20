import tkinter as tk

from PIL import ImageTk

from MahjongTable import MahjongTable
from mahjong_pic.TenhouTable import TenhouTable

table = TenhouTable()
table.load_xml("./paipu/2022scc/scc20220106/2022010616gm-00a9-0000-d4d83e3e.xml")
img_table = MahjongTable()

root = tk.Tk()
root.title("Mahjong")
root.geometry("900x800")
label = tk.Label(root)  # 麻将桌画在标签上
label.pack()

img_index = -1
img_strs = []


def change_img(*arg):
    global img_index, img_strs, label
    if arg[0].delta < 0:  # 向下
        if img_index == len(img_strs) - 1:
            if table.step():
                return
            img_strs.append(table.generate_img())
        img_index += 1
    else:
        if img_index <= 0:
            return
        img_index -= 1

    img_table.fromEasyStr(img_strs[img_index])
    img = img_table.generateImg()
    img = img.resize((800, 800))
    photo = ImageTk.PhotoImage(img)
    label.configure(image=photo)
    label.image = photo


button = tk.Button(root, text='下一张', command=change_img)
button.place(x=0, y=0)
root.bind_all("<MouseWheel>", change_img)

root.mainloop()
