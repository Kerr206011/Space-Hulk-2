takt = 81
hexadezimal = 253
ziel = 4464

while takt < ziel:
    if hexadezimal == 0:
        hexadezimal = 255
    else:
        hexadezimal -=1
    takt += 18

print(takt)
print(hexadezimal)
    