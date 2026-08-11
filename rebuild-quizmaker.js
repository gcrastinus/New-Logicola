/* ============================================================================
   rebuild-quizmaker.js

   quizmaker.html carries a whole copy of LogiCola inside it, so instructors can
   open it on its own without hunting for index.html. This script refreshes that
   copy after you have edited the app.

       node rebuild-quizmaker.js

   Run it from this folder. It reads index.html and writes the copy back into
   quizmaker.html, leaving the quiz maker's own code untouched.

   Nothing breaks if you forget to run it: a stale copy still produces correct
   quizzes, just without whatever exercises you added most recently. And when
   quizmaker.html is served from a web server next to a live index.html, it
   prefers that one anyway and the built-in copy is never used.
   ========================================================================== */

const fs = require('fs');
const path = require('path');

const dir   = __dirname;
const APP   = path.join(dir, 'index.html');
const QUIZ  = path.join(dir, 'quizmaker.html');
const OPEN  = '<script type="text/plain" id="logicola-source">';
const CLOSE = '</' + 'script>';

for(const f of [APP, QUIZ]){
  if(!fs.existsSync(f)){ console.error('Cannot find ' + path.basename(f) + ' in this folder.'); process.exit(1); }
}

const quiz = fs.readFileSync(QUIZ, 'utf8');
const app  = fs.readFileSync(APP, 'utf8');

const start = quiz.indexOf(OPEN);
if(start < 0){ console.error('quizmaker.html has no place to put the copy — is it the right file?'); process.exit(1); }
const from = start + OPEN.length;
const end  = quiz.indexOf(CLOSE, from);
if(end < 0){ console.error('quizmaker.html looks damaged: the embedded copy has no closing tag.'); process.exit(1); }

// The copy is stored as inert text, so its own closing script tag has to be
// hidden from the HTML parser; the quiz maker puts it back when it reads it.
const embedded = app.replace(/<\/script/g, '<\\/script');

// A replacement *function* — a plain string would let $-sequences in the app's
// source rewrite themselves.
const out = quiz.slice(0, from) + embedded + quiz.slice(end);
fs.writeFileSync(QUIZ, out);

const round = out.slice(from, from + embedded.length).replace(/<\\\/script/g, '</script');
if(round !== app){ console.error('Something went wrong: the embedded copy does not read back identically.'); process.exit(1); }

console.log('Refreshed the copy of LogiCola inside quizmaker.html '
  + '(' + Math.round(app.length / 1024) + ' KB, verified byte for byte).');
