import time, random

def cross(A, B): # define la función 'cross'
  "Cross product of elements in A and elements in B."
  return [a + b for a in A for b in B] # regresa un arreglo con el valor de la suma de cada elemento de ambos arreglos

digits = '123456789'        # define los digitos que definen las columnas
rows = 'ABCDEFGHI'          # define las letras que definen las hileras
cols = digits               # renombra la variable de 'digits' a 'cols'
squares = cross(rows, cols) # crea una lista de los diferentes cuadros dentro de la cuadricula del juego

unitlist = (
  [cross(rows, c) for c in cols] +                                            # crea los units de cada hilera 
  [cross(r, cols) for r in rows] +                                            # crea los units de cada columna
  [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')] # crea los units de cada cuadrado de 3x3
) # crea una lista de todos los 'units'

units = dict((s, [u for u in unitlist if s in u]) for s in squares)   # crea un diccionario de cada cuadrado individual con los units a los que pertenece
peers = dict((s, set(sum(units[s],[])) - set([s])) for s in squares)  # crea un diccionario de cada cuadrado individual con sus peers

def parse_grid(grid):
  """Convert grid to a dict of possible values, {square: digits}, or
  return False if a contradiction is detected."""
  ## To start, every square can be any digit; then assign values from the grid.
  values = dict((s, digits) for s in squares)     # crea un diccionario de cada cuadro con todos los posibles valores
  for s, d in grid_values(grid).items():          # itera sobre los valores de cada cuadro, 's' siendo cada cuadro y 'd' su valor
    if d in digits and not assign(values, s, d):  # si ya se encontro el valor de un cuadrado, se asigna en el arreglo de valores
      return False                                # (Fail if we can't assign d to square s.)
  return values # regresa los valores

def grid_values(grid):
  "Convert grid into a dict of {square: char} with '0' or '.' for empties."
  chars = [c for c in grid if c in digits or c in '0.'] # convierte la entrada de string a un arreglo de valores
  assert len(chars) == 81                               # se asegura que la longitud del arreglo sea igual a 81
  return dict(zip(squares, chars))                      # mapea cada cuadrado con su respectivo valor

def assign(values, s, d):
  """Eliminate all the other values (except d) from values[s] and propagate.
  Return values, except return False if a contradiction is detected."""
  other_values = values[s].replace(d, '')                   # crea una lista de todos los valores sin el que se va a asignar
  if all(eliminate(values, s, d2) for d2 in other_values):  # si se logran eliminar todos los valores, se asigna correctamente el valor
    return values
  else:
    return False

def eliminate(values, s, d):
  """Eliminate d from values[s]; propagate when values or places <= 2.
  Return values, except return False if a contradiction is detected."""
  if d not in values[s]:
    return values ## Already eliminated
  values[s] = values[s].replace(d, '') # elimina el mismo valor de todos los cuadrados
  ## (1) If a square s is reduced to one value d2, then eliminate d2 from the peers.
  if len(values[s]) == 0:
    return False ## Contradiction: removed last value
  elif len(values[s]) == 1: # si la longitud es igual a uno, significa que esa es su solución
    d2 = values[s]
    if not all(eliminate(values, s2, d2) for s2 in peers[s]): # elimina el valor de d2 de los demás cuadros
      return False
  ## (2) If a unit u is reduced to only one place for a value d, then put it there.
  for u in units[s]:
    dplaces = [s for s in u if d in values[s]]
    if len(dplaces) == 0:
      return False ## Contradiction: no place for this value
    elif len(dplaces) == 1:
      # d can only be in one place in unit; assign it there
      if not assign(values, dplaces[0], d):
        return False
  return values

def display(values):
  "Display these values as a 2-D grid."
  width = 1 + max(len(values[s]) for s in squares) # 
  line = '----------------+------------------+--------------------' # crea una linea para separar la cuadricula horizonalmente
  print(line)
  for r in rows:
    print ([str(values[r + c].center(width) + ('|' if c in '36' else '')) for c in cols])
    if r in 'CF': print(line)
  print(line)

def solve(grid):
  return search(parse_grid(grid))

def search(values):
  "Using depth-first search and propagation, try all possible values."
  if values is False:
    return False ## Failed earlier
  if all(len(values[s]) == 1 for s in squares):
    return values ## Solved!
  ## Chose the unfilled square s with the fewest possibilities
  n, s = max((len(values[s]), s) for s in squares if len(values[s]) > 1)
  return some(search(assign(values.copy(), s, d)) for d in values[s])
  # return some(search(assign(values.copy(), s, d)) for d in shuffled(values[s]))

def some(seq):
  "Return some element of seq that is true."
  for e in seq:
    if e:
      return e
  return False

def solve_all(grids, name='', showif=0.0):
  """Attempt to solve a sequence of grids. Report results.
  When showif is a number of seconds, display puzzles that take longer.
  When showif is None, don't display any puzzles."""

  def time_solve(grid):
    start = time.time()
    values = solve(grid)
    t = time.time() - start
    
    if values:
      display(values)

    print ('(%f milisegundos)\n' % (t * 1000))

    return (t, solved(values))
  
  times, results = zip( * [time_solve(grid) for grid in grids])
  N = len(grids)
  if N > 1:
    print ("Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs)." % (sum(results), N, name, sum(times) / N, N / sum(times), max(times)))

def solved(values):
  "A puzzle is solved if each unit is a permutation of the digits 1 to 9."
  def unitsolved(unit):
    return set(values[s] for s in unit) == set(digits)
  return values is not False and all(unitsolved(unit) for unit in unitlist)

def random_puzzle(N = 17):
  """Make a random puzzle with N or more assignments. Restart on contradictions.
  Note the resulting puzzle is not guaranteed to be solvable, but empirically
  about 99.8% of them are solvable. Some have multiple solutions."""
  values = dict((s, digits) for s in squares)
  for s in shuffled(squares):
    if not assign(values, s, random.choice(values[s])):
      break
    ds = [values[s] for s in squares if len(values[s]) == 1]
    if len(ds) >= N and len(set(ds)) >= 8:
      return str(values[s] if len(values[s])==1 else '.' for s in squares)
  return random_puzzle(N) ## Give up and make a new puzzle

def shuffled(seq):
  "Return a randomly shuffled copy of the input sequence."
  seq = list(seq)
  random.shuffle(seq)
  return seq

easy_grid =     '8.912.7.4.......8956..4..........6.71.62578.34.2..........8..3172.......9.1.324.6'
medium_grid =   '27..8.........7....415...79.9.62..34...453...42..78.1.91...628....8.........4..91'
hard_grid =     '7..8.........246.3..1..6..2.58..9....3.....4....4..81.8..5..4..2.594.........8..7'
evil_grid =     '7..2...4......8.5.......78...673...5..3.4.1..9...564...37.......6.4......1...5..6'
hardest_grid =  '8..........36......7..9.2...5...7.......457.....1...3...1....68..85...1..9....4..'
profe_grid =    '.....6....59.....82....8....45........3........6..3.54...325..6..................'

if __name__ == '__main__':
  solve_all([easy_grid],    "easy",     None)
  solve_all([medium_grid],  "medium",   None)
  solve_all([hard_grid],    "hard",     None)
  solve_all([evil_grid],    "evil",     None)
  solve_all([hardest_grid], "hardest",  None)
  solve_all([profe_grid],   "profe",    None)

