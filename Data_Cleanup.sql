-- =====================================================
-- INVENTORY DATABASE CLEANUP SCRIPT
-- =====================================================
-- This script performs the following operations:
-- 1. Populates Hitch Type column from Description/Type
-- 2. Removes trailing spaces
-- 3. Removes spaces between letters (H D -> HD)
-- 4. Removes hitch type text from Type and Description
-- 5. Corrects Aluminum spelling variations to ALUM
-- 6. Fixes spacing with FT measurements
-- =====================================================

-- STEP 1: Populate Hitch Type column
-- First, identify Gooseneck from Description
UPDATE inventory
SET hitch_type = 'Gooseneck'
WHERE hitch_type IS NULL 
  AND (
    Description LIKE '%Gooseneck%'
    OR Description LIKE '%Goose neck%'
    OR Description LIKE '%GN%'
    OR Description LIKE '%G/N%'
  );

-- Identify Gooseneck from Type
UPDATE inventory
SET hitch_type = 'Gooseneck'
WHERE hitch_type IS NULL 
  AND (
    type LIKE '%Gooseneck%'
    OR type LIKE '%Goose neck%'
    OR type LIKE '%GN%'
    OR type LIKE '%G/N%'
  );

-- Identify Bumper-pull from Description
UPDATE inventory
SET hitch_type = 'Bumper-pull'
WHERE hitch_type IS NULL 
  AND (
    Description LIKE '%BP%'
    OR Description LIKE '%Bumperpull%'
    OR Description LIKE '%Bumper Pull%'
    OR Description LIKE '%B/P%'
  );

-- Identify Bumper-pull from Type
UPDATE inventory
SET hitch_type = 'Bumper-pull'
WHERE hitch_type IS NULL 
  AND (
    type LIKE '%BP%'
    OR type LIKE '%Bumperpull%'
    OR type LIKE '%Bumper Pull%'
    OR type LIKE '%Bumper-pull%'
    OR type LIKE '%B/P%'
  );

-- Set remaining NULL values to Bumper-pull (default)
UPDATE inventory
SET hitch_type = 'Bumper-pull'
WHERE hitch_type IS NULL;

-- =====================================================
-- STEP 2: Clean up Description field
-- =====================================================

-- Remove Gooseneck variations from Description
UPDATE inventory
SET Description = REPLACE(Description, 'Gooseneck', '')
WHERE Description LIKE '%Gooseneck%';

UPDATE inventory
SET Description = REPLACE(Description, 'Goose neck', '')
WHERE Description LIKE '%Goose neck%';

UPDATE inventory
SET Description = REPLACE(Description, 'goose neck', '')
WHERE Description LIKE '%goose neck%';

UPDATE inventory
SET Description = REPLACE(Description, 'GOOSENECK', '')
WHERE Description LIKE '%GOOSENECK%';

UPDATE inventory
SET Description = REPLACE(Description, 'G/N', '')
WHERE Description LIKE '%G/N%';

UPDATE inventory
SET Description = REPLACE(Description, 'GN ', '')
WHERE Description LIKE '%GN %';

UPDATE inventory
SET Description = REPLACE(Description, ' GN', '')
WHERE Description LIKE '% GN%';

-- Remove Bumper-pull variations from Description
UPDATE inventory
SET Description = REPLACE(Description, 'Bumper Pull', '')
WHERE Description LIKE '%Bumper Pull%';

UPDATE inventory
SET Description = REPLACE(Description, 'Bumperpull', '')
WHERE Description LIKE '%Bumperpull%';

UPDATE inventory
SET Description = REPLACE(Description, 'BUMPER PULL', '')
WHERE Description LIKE '%BUMPER PULL%';

UPDATE inventory
SET Description = REPLACE(Description, 'Bumper-pull', '')
WHERE Description LIKE '%Bumper-pull%';

UPDATE inventory
SET Description = REPLACE(Description, 'B/P', '')
WHERE Description LIKE '%B/P%';

UPDATE inventory
SET Description = REPLACE(Description, 'BP ', '')
WHERE Description LIKE '%BP %';

UPDATE inventory
SET Description = REPLACE(Description, ' BP', '')
WHERE Description LIKE '% BP%';

-- =====================================================
-- STEP 3: Clean up Type field
-- =====================================================

-- Remove Gooseneck variations from Type
UPDATE inventory
SET type = REPLACE(type, 'Gooseneck', '')
WHERE type LIKE '%Gooseneck%';

UPDATE inventory
SET type = REPLACE(type, 'Goose neck', '')
WHERE type LIKE '%Goose neck%';

UPDATE inventory
SET type = REPLACE(type, 'goose neck', '')
WHERE type LIKE '%goose neck%';

UPDATE inventory
SET type = REPLACE(type, 'GOOSENECK', '')
WHERE type LIKE '%GOOSENECK%';

UPDATE inventory
SET type = REPLACE(type, 'G/N', '')
WHERE type LIKE '%G/N%';

UPDATE inventory
SET type = REPLACE(type, 'GN ', '')
WHERE type LIKE '%GN %';

UPDATE inventory
SET type = REPLACE(type, ' GN', '')
WHERE type LIKE '% GN%';

-- Remove Bumper-pull variations from Type
UPDATE inventory
SET type = REPLACE(type, 'Bumper Pull', '')
WHERE type LIKE '%Bumper Pull%';

UPDATE inventory
SET type = REPLACE(type, 'Bumperpull', '')
WHERE type LIKE '%Bumperpull%';

UPDATE inventory
SET type = REPLACE(type, 'BUMPER PULL', '')
WHERE type LIKE '%BUMPER PULL%';

UPDATE inventory
SET type = REPLACE(type, 'Bumper-pull', '')
WHERE type LIKE '%Bumper-pull%';

UPDATE inventory
SET type = REPLACE(type, 'B/P', '')
WHERE type LIKE '%B/P%';

UPDATE inventory
SET type = REPLACE(type, 'BP ', '')
WHERE type LIKE '%BP %';

UPDATE inventory
SET type = REPLACE(type, ' BP', '')
WHERE type LIKE '% BP%';

-- =====================================================
-- STEP 4: Fix Aluminum spelling variations
-- =====================================================

-- Fix in Description field
UPDATE inventory
SET Description = REPLACE(Description, 'ALUIM', 'ALUM')
WHERE Description LIKE '%ALUIM%';

UPDATE inventory
SET Description = REPLACE(Description, 'ALIUM', 'ALUM')
WHERE Description LIKE '%ALIUM%';

UPDATE inventory
SET Description = REPLACE(Description, 'Aluminum', 'ALUM')
WHERE Description LIKE '%Aluminum%';

UPDATE inventory
SET Description = REPLACE(Description, 'aluminum', 'ALUM')
WHERE Description LIKE '%aluminum%';

UPDATE inventory
SET Description = REPLACE(Description, 'ALUMINUM', 'ALUM')
WHERE Description LIKE '%ALUMINUM%';

-- Fix in Type field
UPDATE inventory
SET type = REPLACE(type, 'ALUIM', 'ALUM')
WHERE type LIKE '%ALUIM%';

UPDATE inventory
SET type = REPLACE(type, 'ALIUM', 'ALUM')
WHERE type LIKE '%ALIUM%';

UPDATE inventory
SET type = REPLACE(type, 'Aluminum', 'ALUM')
WHERE type LIKE '%Aluminum%';

UPDATE inventory
SET type = REPLACE(type, 'aluminum', 'ALUM')
WHERE type LIKE '%aluminum%';

UPDATE inventory
SET type = REPLACE(type, 'ALUMINUM', 'ALUM')
WHERE type LIKE '%ALUMINUM%';

-- =====================================================
-- STEP 5: Fix FT spacing issues
-- =====================================================

-- Fix "8 FT" -> "8FT" in Description (for numbers 1-99)
UPDATE inventory
SET Description = REPLACE(Description, '0 FT', '0FT');
UPDATE inventory
SET Description = REPLACE(Description, '1 FT', '1FT');
UPDATE inventory
SET Description = REPLACE(Description, '2 FT', '2FT');
UPDATE inventory
SET Description = REPLACE(Description, '3 FT', '3FT');
UPDATE inventory
SET Description = REPLACE(Description, '4 FT', '4FT');
UPDATE inventory
SET Description = REPLACE(Description, '5 FT', '5FT');
UPDATE inventory
SET Description = REPLACE(Description, '6 FT', '6FT');
UPDATE inventory
SET Description = REPLACE(Description, '7 FT', '7FT');
UPDATE inventory
SET Description = REPLACE(Description, '8 FT', '8FT');
UPDATE inventory
SET Description = REPLACE(Description, '9 FT', '9FT');

-- Fix "8.FT" -> "8FT" in Description
UPDATE inventory
SET Description = REPLACE(Description, '0.FT', '0FT');
UPDATE inventory
SET Description = REPLACE(Description, '1.FT', '1FT');
UPDATE inventory
SET Description = REPLACE(Description, '2.FT', '2FT');
UPDATE inventory
SET Description = REPLACE(Description, '3.FT', '3FT');
UPDATE inventory
SET Description = REPLACE(Description, '4.FT', '4FT');
UPDATE inventory
SET Description = REPLACE(Description, '5.FT', '5FT');
UPDATE inventory
SET Description = REPLACE(Description, '6.FT', '6FT');
UPDATE inventory
SET Description = REPLACE(Description, '7.FT', '7FT');
UPDATE inventory
SET Description = REPLACE(Description, '8.FT', '8FT');
UPDATE inventory
SET Description = REPLACE(Description, '9.FT', '9FT');

-- Fix "8 FT" -> "8FT" in Type
UPDATE inventory
SET type = REPLACE(type, '0 FT', '0FT');
UPDATE inventory
SET type = REPLACE(type, '1 FT', '1FT');
UPDATE inventory
SET type = REPLACE(type, '2 FT', '2FT');
UPDATE inventory
SET type = REPLACE(type, '3 FT', '3FT');
UPDATE inventory
SET type = REPLACE(type, '4 FT', '4FT');
UPDATE inventory
SET type = REPLACE(type, '5 FT', '5FT');
UPDATE inventory
SET type = REPLACE(type, '6 FT', '6FT');
UPDATE inventory
SET type = REPLACE(type, '7 FT', '7FT');
UPDATE inventory
SET type = REPLACE(type, '8 FT', '8FT');
UPDATE inventory
SET type = REPLACE(type, '9 FT', '9FT');

-- Fix "8.FT" -> "8FT" in Type
UPDATE inventory
SET type = REPLACE(type, '0.FT', '0FT');
UPDATE inventory
SET type = REPLACE(type, '1.FT', '1FT');
UPDATE inventory
SET type = REPLACE(type, '2.FT', '2FT');
UPDATE inventory
SET type = REPLACE(type, '3.FT', '3FT');
UPDATE inventory
SET type = REPLACE(type, '4.FT', '4FT');
UPDATE inventory
SET type = REPLACE(type, '5.FT', '5FT');
UPDATE inventory
SET type = REPLACE(type, '6.FT', '6FT');
UPDATE inventory
SET type = REPLACE(type, '7.FT', '7FT');
UPDATE inventory
SET type = REPLACE(type, '8.FT', '8FT');
UPDATE inventory
SET type = REPLACE(type, '9.FT', '9FT');

-- =====================================================
-- STEP 6: Remove spaces between individual letters
-- =====================================================

-- This removes patterns like "H D" -> "HD"
-- Note: This is a simplified approach that removes space between 
-- single capital letters. Adjust patterns as needed for your data.

UPDATE inventory
SET Description = REPLACE(Description, 'H D', 'HD')
WHERE Description LIKE '% H D %' OR Description LIKE 'H D %' OR Description LIKE '% H D';

UPDATE inventory
SET type = REPLACE(type, 'H D', 'HD')
WHERE type LIKE '% H D %' OR type LIKE 'H D %' OR type LIKE '% H D';

-- Add more letter combinations if you have specific patterns
-- For example:
-- UPDATE inventory SET Description = REPLACE(Description, 'L P', 'LP');
-- UPDATE inventory SET type = REPLACE(type, 'L P', 'LP');

-- =====================================================
-- STEP 7: Remove trailing spaces from all text fields
-- =====================================================

UPDATE inventory
SET Description = TRIM(Description)
WHERE Description IS NOT NULL;

UPDATE inventory
SET type = TRIM(type)
WHERE type IS NOT NULL;

UPDATE inventory
SET make = TRIM(make)
WHERE make IS NOT NULL;

UPDATE inventory
SET dimensions = TRIM(dimensions)
WHERE dimensions IS NOT NULL;

UPDATE inventory
SET capacity = TRIM(capacity)
WHERE capacity IS NOT NULL;

UPDATE inventory
SET condition = TRIM(condition)
WHERE condition IS NOT NULL;

UPDATE inventory
SET vin = TRIM(vin)
WHERE vin IS NOT NULL;

UPDATE inventory
SET color = TRIM(color)
WHERE color IS NOT NULL;

-- =====================================================
-- STEP 8: Clean up multiple spaces
-- =====================================================

-- Replace multiple spaces with single space in Description
UPDATE inventory
SET Description = REPLACE(REPLACE(REPLACE(Description, '   ', ' '), '  ', ' '), '  ', ' ')
WHERE Description LIKE '%  %';

-- Replace multiple spaces with single space in Type
UPDATE inventory
SET type = REPLACE(REPLACE(REPLACE(type, '   ', ' '), '  ', ' '), '  ', ' ')
WHERE type LIKE '%  %';

-- =====================================================
-- STEP 9: View summary of results
-- =====================================================

SELECT 
  'Hitch Type Distribution' as summary_type,
  hitch_type,
  COUNT(*) as count
FROM inventory
GROUP BY hitch_type
ORDER BY hitch_type;
