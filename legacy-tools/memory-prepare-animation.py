from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'experiments.sema').read_text()
s=s.replace('(define records', '(define wave 0.0)\n(define sway 0.0)\n(define records',1)
a=s.index('(define (save name)');b=s.index(';; Each five-port',a)
s=s[:a]+'''(define (save name)
  (println "BEGIN")
  (println (string/join (reverse records) "\\n"))
  (println "END")
  (set! records '()))
\n'''+s[b:]
s=s.replace('(lace 600 600 315 -1.57079632679 6 0)\n(save "address-lace")','')
s=s.replace('(braid 600 600 355 -1.57079632679 0.6 6 0)\n(save "signed-braid")','')
a=s.index('(for-each (fn (arm)');s=s[:a]
s=s.replace('(* 0.31 (sin (* 2 phase)))','(* 0.31 (sin (* 2 phase))) (* 0.065 wave (- port 2))')
s=s.replace('(bend (+ 0.35 (* 0.22 (sin memory)))))','(bend (+ 0.35 (* 0.22 (sin memory)) (* 0.04 sway)))\n           (segments (if (< level 2) 96 (if (< level 4) 32 12))))')
s=s.replace('(/ j 12)','(/ j segments)').replace('(/ (+ j 1) 12)','(/ (+ j 1) segments)').replace('(range 12)','(range segments)')
s=s.replace('(- k 1) 0.27)','(- k 1) 0.27 (* 0.085 wave sign))')
s=s.replace('(turn (* 0.48 (sin phase)))','(turn (* 0.48 (sin phase)))\n         (segments (if (< level 2) 48 (if (< level 4) 16 8)))')
s=s.replace('(/ j 8)','(/ j segments)').replace('(/ (+ j 1) 8)','(/ (+ j 1) segments)').replace('(range 8)','(range segments)')
s=s.replace('(* 0.25 (sin phase)))','(* 0.25 (sin phase)) (* 0.08 wave (- port 1.5)))')
starts={
'address-lace':'(lace 600 600 315 (+ -1.57079632679 (* 0.22 wave)) 6 0)',
'signed-braid':'(braid 600 600 355 (+ -1.57079632679 (* 0.12 sway)) (+ 0.6 (* 0.38 wave)) 6 0)',
'phase-coral':'''(for-each (fn (arm)
  (coral 600 600 190 (+ -1.57079632679 (* tau (/ arm 7)) (* 0.10 sway))
    (+ 0.41 (* arm 0.73) (* 0.32 wave)) 5 0)) (range 7))'''}
for name,start in starts.items():
 tail='''\n(for-each (fn (frame)
  (let ((theta (* tau (/ frame 48))))
    (set! wave (sin theta))
    (set! sway (- (cos theta) 1))
    START
    (save "NAME"))) (range 48))\n'''.replace('START',start).replace('NAME',name)
 (r/(name+'-loop.sema')).write_text(s+tail)
print('Prepared 48 periodic keyframes per construction.')
