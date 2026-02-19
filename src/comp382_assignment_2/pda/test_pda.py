# Add project root to path
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from comp382_assignment_2.pda.example_pda import create_an_bn_pda

def test_pda():
    pda = create_an_bn_pda()
    input_str = "aabb"
    pda.load_input(input_str)
    
    print(f"Testing PDA with input: {input_str}")
    print(f"Initial State: {pda.current_state}, Stack: {pda.stack}")
    
    while True:
        prev_state = pda.current_state
        prev_stack = list(pda.stack)
        if not pda.step():
            break
        print(f"Stepped: {prev_state} -> {pda.current_state}, Stack: {pda.stack}")
        
    if pda.is_accepted():
        print("Result: Accepted!")
    else:
        print(f"Result: Rejected (State: {pda.current_state}, Index: {pda.input_index}/{len(input_str)})")

if __name__ == "__main__":
    test_pda()
