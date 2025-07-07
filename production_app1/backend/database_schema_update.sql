-- Add login OTP columns to users table if they don't exist
ALTER TABLE users ADD COLUMN login_otp TEXT;
ALTER TABLE users ADD COLUMN login_otp_expires INTEGER;