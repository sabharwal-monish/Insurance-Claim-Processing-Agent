-- Insurance Claim Processing Agent - Database Schema
-- Database: Aiven MySQL with SSL
-- Last Updated: 2026-01-20

CREATE TABLE IF NOT EXISTS insurance_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    policy_number VARCHAR(50) DEFAULT NULL,
    claimant_name VARCHAR(255) DEFAULT NULL,
    date_time_of_incident VARCHAR(255) DEFAULT NULL,
    vehicle_info TEXT DEFAULT NULL,
    incident_description TEXT DEFAULT NULL,
    photo_uploaded BOOLEAN DEFAULT FALSE,
    damage_report TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_policy_number (policy_number),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;