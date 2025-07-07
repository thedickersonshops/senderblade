"""
Simple Math Captcha for SenderBlade
Easy, effective, no external dependencies
"""
import random
import hashlib

class SimpleCaptcha:
    """Simple math captcha generator"""
    
    @staticmethod
    def generate_math_captcha():
        """Generate a simple math problem"""
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        operation = random.choice(['+', '-'])
        
        if operation == '+':
            answer = num1 + num2
            question = f"What is {num1} + {num2}?"
        else:
            # Ensure positive result for subtraction
            if num1 < num2:
                num1, num2 = num2, num1
            answer = num1 - num2
            question = f"What is {num1} - {num2}?"
        
        # Create a hash of the answer for verification
        answer_hash = hashlib.md5(str(answer).encode()).hexdigest()
        
        return {
            'question': question,
            'answer_hash': answer_hash,
            'answer': answer  # For testing only, remove in production
        }
    
    @staticmethod
    def verify_captcha(user_answer, answer_hash):
        """Verify captcha answer"""
        try:
            user_answer = int(user_answer)
            user_hash = hashlib.md5(str(user_answer).encode()).hexdigest()
            return user_hash == answer_hash
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def get_captcha_html(captcha_data):
        """Get HTML for captcha display"""
        return f'''
        <div class="mb-3">
            <label class="form-label">🔐 Security Check</label>
            <p class="text-muted">{captcha_data['question']}</p>
            <input type="number" class="form-control" id="captcha_answer" name="captcha_answer" 
                   placeholder="Enter your answer" required>
            <input type="hidden" id="captcha_hash" name="captcha_hash" value="{captcha_data['answer_hash']}">
            <small class="text-muted">Please solve this simple math problem to continue</small>
        </div>
        '''

# Test the captcha
if __name__ == "__main__":
    captcha = SimpleCaptcha()
    test_captcha = captcha.generate_math_captcha()
    print("Question:", test_captcha['question'])
    print("Answer:", test_captcha['answer'])
    print("Hash:", test_captcha['answer_hash'])
    
    # Test verification
    print("Verification test:", captcha.verify_captcha(test_captcha['answer'], test_captcha['answer_hash']))