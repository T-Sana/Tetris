from tsanap import *
class endGame(Exception): ...
class mouse:
    click = False
    pos = [-1, -1]

def get_cases(pos) -> tuple:
    return ([int(i) for i in[(pos[0]-mmp.p1[0])/dist(mmp.p1,mmp.p2)*3,(pos[1]-mmp.p1[1])/dist(mmp.p1,mmp.p3)*3]] for n in [3, mmp.cases])

def get_mouse(event, x, y, flags, params) -> None:
    if event == cv2.EVENT_LBUTTONDOWN:
        pos = [x,y]
        if clicked_in(pos, [mmp.p1, mmp.p4]):
            mouse.game = [int(i) for i in [(pos[0]-mmp.p1[0])/dist(mmp.p1, mmp.p2)*3, (pos[1]-mmp.p1[1])/dist(mmp.p1, mmp.p3)*3]]
            mouse.case = [int(i) for i in [(pos[0]-mmp.p1[0])/dist(mmp.p1, mmp.p2)*mmp.cases, (pos[1]-mmp.p1[1])/dist(mmp.p1, mmp.p3)*mmp.cases]]
    if event == cv2.EVENT_LBUTTONUP:
        pos = [x, y]
        if clicked_in(pos, [mmp.p1, mmp.p4]):
            game = [int(i) for i in [(pos[0]-mmp.p1[0])/dist(mmp.p1, mmp.p2)*3, (pos[1]-mmp.p1[1])/dist(mmp.p1, mmp.p3)*3]]
            case = [int(i) for i in [(pos[0]-mmp.p1[0])/dist(mmp.p1, mmp.p2)*mmp.cases, (pos[1]-mmp.p1[1])/dist(mmp.p1, mmp.p3)*mmp.cases]]
            if case == mouse.case: mouse.click = True


class mmp: ## Maximorpion (MMP)
    p1, p2 = [screen[0]/2-screen[1]/2, 0], [screen[0]/2+screen[1]/2, 0]
    p3, p4 = [screen[0]/2-screen[1]/2, screen[1]], [screen[0]/2+screen[1]/2, screen[1]]
    cases, fs = 9, False

    def __init__(self, name="MaxiMorpion") -> None:
        self.name = name; self.x, self.y = 9, 9
        self.matrix = np.array([[0 for _ in range(self.x)] for _ in range(self.y)])
        self.trait = True
        self.lastm = -1
        self.winner = -1
        self.wgames = [0, 0]

    def restart(self, trait=None) -> None:
        self.matrix = np.array([[0 for _ in range(self.x)] for _ in range(self.y)])
        self.trait = True if trait == None else trait
        self.lastm = -1
        self.winner = -1
        mouse.click = False
        mouse.pos = [-1, -1]

    def __str__(self) -> str:
        return "\n".join(" ".join(str(self.matrix[x,y]) for x in range(self.x)) for y in range(self.y))
    
    def image(self) -> image:
        img = image(nom=self.name, img=image.new_img(fond=col.green, dimensions=screen))
        p1, p2, p3, p4 = self.p1, self.p2, self.p3, self.p4
        c = [0, 3, 6, 9]
        X = [p1[0]+(p4[0]-p1[0])/self.cases*n for n in range(self.cases)] + [p4[0]]
        Y = [p1[1]+(p4[1]-p1[1])/self.cases*n for n in range(self.cases)] + [p4[1]]
        for n, x in enumerate(X): img.ligne([x, p1[1]], [x, p4[1]], col.noir, 10 if n in c else 3, 2)
        for n, y in enumerate(Y): img.ligne([p1[0], y], [p4[0], y], col.noir, 10 if n in c else 3, 2)
        for x in range(9):
            for y in range(9):
                c = self.matrix[x,y]
                if c==0: continue
                img.ecris("x" if c==1 else "o", [moyenne(X[x], X[x+1]), moyenne(Y[y], Y[y+1])], col.blue if c==1 else col.red, 5, 5, cv2.FONT_HERSHEY_SIMPLEX, 2)
        img.ecris(f"A {"X" if self.trait else "O"} de\njouer", ct_sg([0, 0], p3), col.blue if self.trait else col.red, 3, 2, cv2.FONT_HERSHEY_SIMPLEX, 2)
        img.ecris(f"X: {self.wgames[0]}\n", ct_sg(p2, screen), col.blue, 3, 2, cv2.FONT_HERSHEY_SIMPLEX, 2)
        img.ecris(f"\nO: {self.wgames[1]}", ct_sg(p2, screen), col.red,  3, 2, cv2.FONT_HERSHEY_SIMPLEX, 2)
        return img

    def finished(self) -> bool:
        for game in [self.matrix[x:x+3, y:y+3] for x in range(0,9,3) for y in range(0,9,3)]:
            M = [game[0:3, n] for n in range(3)] + [game[n, 0:3] for n in range(3)]
            M += [[game[n, n] for n in range(3)],  [game[2-n, n] for n in range(3)]]
            for m in M:
                if not 0 in set(m) and len(set(m)) == 1:
                    self.winner = m[0]
                    self.wgames[m[0]-1] += 1
                    return True 
        return False

    def playable(self) -> bool:
        if not 0 in self.matrix:
            return self.finished()
        return True

    def legal(self, game, case) -> bool:
        if self.lastm in [-1, game]:
            if self.matrix[case[0],case[1]] == 0:
                return True
        return False

    def game(self) -> None:
        img = self.image()
        img.montre(1, fullscreen=mmp.fs)
        cv2.setMouseCallback(img.nom, get_mouse)
        while self.playable() and not self.finished():
            if mouse.click:
                if self.legal(mouse.game, mouse.case):
                    self.matrix[mouse.case[0], mouse.case[1]] = 1 if self.trait else 2
                    self.lastm = [i%3 for i in mouse.case]
                    self.trait = not self.trait
                    img = self.image()
                mouse.click = False
            wk = img.montre(1, fullscreen=mmp.fs)
            if img.is_closed(): raise endGame
            match wk:
                case 27: raise endGame
                case 32 | 8: mmp.fs = not mmp.fs
                case 114: return self.restart(True)
                case -1: ...
                case 65470: cv2.moveWindow(img.nom, 0, 0) ## f1
                case 65471: cv2.moveWindow(img.nom, screen[0], 0) ## f2
        img = self.image()
        img.ecris(f"{"J1" if self.winner == 1 else "J2"} won!", ct_sg(mmp.p1, mmp.p4), col.red, 12, 3, lineType=2)
        img.ecris(f"{"J1" if self.winner == 1 else "J2"} won!", ct_sg(mmp.p1, mmp.p4), col.black, 5, 3, lineType=2)
        while True:
            wk = img.montre(1, fullscreen=mmp.fs)
            if img.is_closed(): raise endGame
            match wk:
                case 27: raise endGame
                case 32 | 8: mmp.fs = not mmp.fs
                case -1: ...
                case _: return self.restart()

    def start(self) -> None:
        while True: 
            try: self.game()
            except endGame: return

def main():
    jeu = mmp()
    jeu.start()
    

if __name__ == "__main__":
    main()