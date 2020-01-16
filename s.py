#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import time

sys.path.append( '/root/python' )

from blessed import Terminal

HORIZ_SPACING = 5
VERT_SPACING = 2
GRID_HORIZ_START = 8
GRID_VERT_START = 3

t = Terminal()

s = [
     0, 7, 0, 0, 0, 8, 0, 0, 0,
     0, 0, 2, 0, 0, 0, 0, 1, 7,
     0, 0, 0, 0, 5, 0, 0, 0, 0,
     0, 9, 0, 0, 0, 0, 0, 6, 0,
     0, 2, 7, 0, 0, 9, 0, 0, 0,
     0, 0, 3, 8, 0, 7, 0, 5, 9,
     0, 0, 0, 1, 0, 0, 0, 0, 3,
     0, 0, 0, 9, 0, 0, 0, 0, 0,
     6, 5, 0, 0, 0, 0, 2, 9, 0 ]

debug_msg_buffer = [ None ] * 82
debug_height = 9
debug_slider = 0
clash = [ None ] * 81
 
for line in range( 0, 82 ):
    debug_msg_buffer[ line ] = " "

# debug_msg shows the most recent debug message at each level, with up to debug_height lines
# visible.
def debug_msg( msg, level=0 ):

    global debug_slider

    msg = "At cell %2d: %s" % ( level, msg )
    debug_msg_buffer[ level ] = msg

    if ( ( ( level - debug_slider ) < debug_height ) and ( ( level - debug_slider ) >= 0 ) ):
        
        sys.stdout.write( t.move( t.height - ( 2 + level - debug_slider ), 5 ) + msg )
        sys.stdout.flush()

    else:

        if ( ( level - debug_slider ) > ( debug_height - 1) ):
            debug_slider = level - debug_height + 1 

        elif ( ( level - debug_slider ) < 0  ):
            debug_slider = level

        for row in range( 0, debug_height ):
    
            sys.stdout.write( t.move( t.height - ( 2 + row ), 5 ) + debug_msg_buffer[ row + debug_slider ] )
            sys.stdout.flush()
            
# Convert a flat index into the s[] array, to coordinates in the Sudoku matrix
def index_to_coord( index ):

    return( index % 9, index // 9 )

# ... and vice versa
def coord_to_index( x, y ):

    return( y * 9 + x )

# Calculates the x,y position on screen for a coordinate in the Sudoku matrix
def coord_to_screen_pos( x, y ):

    return( y * VERT_SPACING + GRID_VERT_START, x * HORIZ_SPACING + GRID_HORIZ_START )

# Returns the top-left coordinate position of the 9x9 box enclosing a given cell.
def coord_to_9box_start_coord( x, y ):
    
    return (  x // 3  * 3 ,  y // 3 * 3 )

# This isn't part of the solution itself.  Rather it creates a lookup table.  I could have hard coded this
# as static data because it never changes, but its fun to calculate anyway.
def populate_clash():

    for index in range( 0, 81 ):

        twenty = [ None ] * 20
        count_20 = 0
 
        ( x, y ) = index_to_coord( index )
    
        # For every possible index value there are 20 possible other index values
        # which directly clash either on the same row, column, or 9box

        # Start at the top of the column containing the cell and work down.
        for count_down in range( 0, 9 ):
 
            # We need to check to ensure we don't mark (x,y) cell as clashing with itself
            if ( count_down == y ):
 
                continue
 
            # There are nine cells in the column, but after skipping the cell itself
            # we should end up adding 8 cells to this list in this for loop
            twenty[ count_20 ] = coord_to_index( x, count_down )
            count_20 += 1
 
        # Now check all the cells in the same row as the cell, skipping the (x,y) cell itself
        for count_across in range( 0, 9 ):
 
            if ( count_across == x ):
                continue
 
            twenty[ count_20 ] = coord_to_index( count_across, y )
            count_20 += 1
 
        # Check the (x,y) cell against the cells in the same 9box group is more complicated
        # because these cells are not all contiguous and some have already been added to the
        # list of potential clashes.  There should be four to add to the list after excluding
        # (x,y) itself and the cells which are either in the same row or column
        ( box_start_x, box_start_y ) = coord_to_9box_start_coord( x, y ) 

        # Initially set our current position to the top left of the box we are checking
        ( box_current_x, box_current_y ) = ( box_start_x, box_start_y )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        # Now check the top middle
        ( box_current_x, box_current_y ) = ( box_start_x + 1, box_start_y )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        # Now check the top right corner
        ( box_current_x, box_current_y ) = ( box_start_x + 2, box_start_y )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        # Now check the middle left
        ( box_current_x, box_current_y ) = ( box_start_x, box_start_y + 1 )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        # Now check the centre cell
        ( box_current_x, box_current_y ) = ( box_start_x + 1, box_start_y + 1 )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        # Now check the middle right
        ( box_current_x, box_current_y ) = ( box_start_x + 2, box_start_y + 1 )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        # Now check the bottom left
        ( box_current_x, box_current_y ) = ( box_start_x, box_start_y + 2 )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        # Now check the bottom middle
        ( box_current_x, box_current_y ) = ( box_start_x + 1, box_start_y + 2 )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        # Now check the bottom right corner
        ( box_current_x, box_current_y ) = ( box_start_x + 2, box_start_y + 2 )
 
        if ( box_current_x !=  x ):
            if ( box_current_y !=  y ):
                twenty[ count_20 ] = coord_to_index( box_current_x, box_current_y )
                count_20 += 1

        clash[ index ] = twenty
 
def print_cell( i, str, bold=0 ):

   ( x, y ) = index_to_coord( i )
   ( v, h ) = coord_to_screen_pos( x, y )
   if ( str == '0' ):
      str = ' '
   if ( bold == 0 ):
       sys.stdout.write( t.move( v, h ) + str )
   else:
       sys.stdout.write( t.move( v, h ) + t.bold_yellow( str ) )

   sys.stdout.flush()

def print_lines():

    sys.stdout.write ( t.move(  2, 2 ) + u"   ╔════╤════╤════╦════╤════╤════╦════╤════╤════╗" )
    sys.stdout.write ( t.move(  3, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move(  4, 2 ) + u"   ╟────┼────┼────╫────┼────┼────╫────┼────┼────╢" )
    sys.stdout.write ( t.move(  5, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move(  6, 2 ) + u"   ╟────┼────┼────╫────┼────┼────╫────┼────┼────╢" )
    sys.stdout.write ( t.move(  7, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move(  8, 2 ) + u"   ╠════╪════╪════╬════╪════╪════╬════╪════╪════╣" )
    sys.stdout.write ( t.move(  9, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move( 10, 2 ) + u"   ╟────┼────┼────╫────┼────┼────╫────┼────┼────╢" )
    sys.stdout.write ( t.move( 11, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move( 12, 2 ) + u"   ╟────┼────┼────╫────┼────┼────╫────┼────┼────╢" )
    sys.stdout.write ( t.move( 13, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move( 14, 2 ) + u"   ╠════╪════╪════╬════╪════╪════╬════╪════╪════╣" )
    sys.stdout.write ( t.move( 15, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move( 16, 2 ) + u"   ╟────┼────┼────╫────┼────┼────╫────┼────┼────╢" )
    sys.stdout.write ( t.move( 17, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move( 18, 2 ) + u"   ╟────┼────┼────╫────┼────┼────╫────┼────┼────╢" )
    sys.stdout.write ( t.move( 19, 2 ) + u"   ║    │    │    ║    │    │    ║    │    │    ║" )
    sys.stdout.write ( t.move( 20, 2 ) + u"   ╚════╧════╧════╩════╧════╧════╩════╧════╧════╝" )
    sys.stdout.flush()

# This function is not actually used, but was created for debugging
def show_clash_table():

    for index in range( 0, 81 ):

        my_clashes = clash[ index ]
        print_cell( index, "X" )
        
        for count in range( 0, 20 ):

            print_cell( my_clashes[ count ], "#" )

            #debug_msg( "count is %d" % count )

            time.sleep( 0.1 )

        #debug_msg( "index is %d" % index )
        time.sleep( 0.01 ) 

        print_cell( index, " " )
        for count in range( 0, 20 ):

            print_cell( my_clashes[ count ], " " )

def solve_it( index ):

    debug_msg( "solve_it() started with index = %d" % index, index )

    # This function is called recursively for each unknown cell.  If we reach the end of the
    # array then we have succeeded and return.  Once the deepest level instance of this 
    # function returns True then the whole stack will unwind back the first cell and
    # mission accomplished.
    if ( index > 80 ):
        return( True )

    # In the index passed is for a cell which is already known then we need to skip forward to
    # the next unset call.  
    while ( s[ index ] != 0 ):
        debug_msg( "skipping cell containing known number", index )
        index += 1

    # Get the list of cells which mustn't have the same number as s[index]
    my_clashes = clash[ index ]

    # Test each number from 1 to 9, comparing each to the clash list (20 possibilities)
    for try_me in range( 1, 10 ):

        good_flag = True
        for check in range( 0, 20 ):

           if ( try_me == s[ my_clashes[ check ] ] ):

               good_flag = False
               # If any of the 20 possible clashes occur then that is a failure and we can skip rest
               break

        # This point can be reached either via the break statement above, in which case good_flag is
        # False, or because there were no clashes after checking all possibilities.  If there was a
        # clash then good is False and we need to continue on to the next number in range ( 0, 20 )
        if ( good_flag is False ):
            continue

        # If we've reached here then try_me doesn't clash with any of the 20 possible cells.
        # So pencil that value into s[ index ] and call solve_it() for the next highest cell
        s[ index ] = try_me
        #print_cell( index, chr( ord( '0' ) + try_me ) )
        print_cell( index, str(try_me) )

        if ( solve_it( index + 1 ) ):

            # Any solve_it() child which returns True means that the number we pencilled in 
            # is definitely correct so we can in turn return True
            debug_msg( "solve_it() returning True                ", index )
            return( True )
 
        else:
           # Erase the number we penciled in earlier because we know that numbmer is not correct.
           s[ index ] = 0
           print_cell( index, ' ', bold=0  )

        # Reaching here means that we carry on and try the next hightest number (1 to 9) 

    # Reaching here means that every number from 1 - 9 was unsuitable.  Return False
    # because one of the lower down pencilled in numbers must be wrong--or the puzzle
    # cannot be solved
    debug_msg( "solve_it() returning False                ", index )
    return( False )

populate_clash()

with t.fullscreen():
  with t.hidden_cursor():
    print_lines()

    for print_index in range( 0, 81 ):
        #print_cell( print_index, chr( ord( '0' ) + s[ print_index ] ), bold=1  )
        print_cell( print_index, str(s[ print_index ]), bold=1  )

    sys.stdout.write(t.move(t.height // 2, 6 ) + 'Press <ENTER> to solve this Sudoku!')
    sys.stdout.flush()
    t.inkey( )

    if ( solve_it( 0 ) is True ):
        debug_msg( "Solved!!!!!!!!!!!!!!!!!!!!!!!!!", 0 )
    else:
        debug_msg( "Failed to find a solution!!!!!!", 0 )

    t.inkey()

