from pathlib import Path
r=(Path(__file__).resolve().parent.parent / 'splash-fractals')
s=(r/'gallery.sema').read_text().split('(render 0 "folded-crown")')[0]
s=s.replace('(define width 840)','(define width 360)').replace('(define height 640)','(define height 274)').replace('(define limit 100)','(define limit 65)\n(define phase 0.0)\n(define drift 0.0)\n(define sway 0.0)')
s=s.replace('0.62)))','(+ 0.62 (* 0.04 sway)))))')
s=s.replace(' -0.38)',' (+ -0.38 (* 0.035 drift)))').replace(' 0.12)',' (+ 0.12 (* 0.025 sway)))')
s=s.replace(' -0.69)',' (+ -0.69 (* 0.025 drift)))').replace(' 0.19) (+ n',' (+ 0.19 (* 0.025 sway))) (+ n')
s=s.replace('(+ x 0.23)','(+ x 0.23 (* 0.025 drift))').replace('(- y 0.11)','(- y 0.11 (* 0.025 sway))')
for mode,name in enumerate(['folded-crown','alternating-tide','pole-garden']):
    (r/(name+'-frames')).mkdir(exist_ok=True)
    tail=f'''\n(for-each (fn (frame)
  (set! phase (* 6.283185307179586 (/ frame 32)))
  (set! drift (sin phase))
  (set! sway (- (cos phase) 1))
  (render {mode} (str "{name}-frames/" (string/pad-left (str frame) 3 "0")))) (range 32))
'''
    (r/(name+'-animation.sema')).write_text(s+tail)
print('Prepared three 32-frame Sema animations.')
