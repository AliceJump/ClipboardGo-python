import qrcode

img = qrcode.make("https://zh.minecraft.wiki/")
img.save("qrcode.png")
