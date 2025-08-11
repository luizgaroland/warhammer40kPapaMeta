-- =====================================================
-- WARHAMMER 40K META ANALYSIS DATABASE
-- Optimized for 10th Edition and Wahapedia Scraping
-- =====================================================

-- Drop existing tables if needed (comment out in production)
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

-- =====================================================
-- CORE VERSION TRACKING TABLES
-- =====================================================

-- Major game versions (e.g., 9th Edition, 10th Edition)
CREATE TABLE warhammer_major_versions (
   id SERIAL PRIMARY KEY,
   version_number VARCHAR(20) NOT NULL UNIQUE,
   name VARCHAR(100) NOT NULL,
   release_date DATE NOT NULL,
   is_current BOOLEAN DEFAULT FALSE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Balance updates/erratas/dataslates within a major version
CREATE TABLE warhammer_updates (
   id SERIAL PRIMARY KEY,
   major_version_id INTEGER NOT NULL REFERENCES warhammer_major_versions(id) ON DELETE CASCADE,
   update_type VARCHAR(50) NOT NULL, -- 'errata', 'dataslate', 'faq', 'mfm', 'codex'
   version_code VARCHAR(50) NOT NULL,
   name VARCHAR(200) NOT NULL,
   release_date DATE NOT NULL,
   is_current BOOLEAN DEFAULT FALSE,
   change_summary TEXT,
   source_url TEXT, -- Link to official announcement
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(major_version_id, version_code)
);

-- Combined version snapshot for tracking unit/faction states
CREATE TABLE version_snapshots (
   id SERIAL PRIMARY KEY,
   major_version_id INTEGER NOT NULL REFERENCES warhammer_major_versions(id) ON DELETE CASCADE,
   update_id INTEGER REFERENCES warhammer_updates(id) ON DELETE CASCADE,
   effective_date DATE NOT NULL,
   is_current BOOLEAN DEFAULT FALSE,
   snapshot_hash VARCHAR(64), -- For change detection
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(major_version_id, update_id)
);

-- =====================================================
-- FACTION STRUCTURE TABLES
-- =====================================================

-- Base faction definitions
CREATE TABLE factions (
   id SERIAL PRIMARY KEY,
   name VARCHAR(100) NOT NULL,
   code VARCHAR(50) NOT NULL UNIQUE,
   full_name VARCHAR(200), -- e.g., "Adeptus Astartes" for Space Marines
   is_active BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Faction states at specific versions
CREATE TABLE faction_versions (
   id SERIAL PRIMARY KEY,
   faction_id INTEGER NOT NULL REFERENCES factions(id) ON DELETE CASCADE,
   version_snapshot_id INTEGER NOT NULL REFERENCES version_snapshots(id) ON DELETE CASCADE,
   has_codex BOOLEAN DEFAULT FALSE, -- 10th edition tracking
   codex_release_date DATE,
   is_playable BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(faction_id, version_snapshot_id)
);

-- Army rules (10th edition - one per faction)
CREATE TABLE army_rules (
   id SERIAL PRIMARY KEY,
   faction_version_id INTEGER NOT NULL REFERENCES faction_versions(id) ON DELETE CASCADE,
   name VARCHAR(200) NOT NULL,
   rule_type VARCHAR(50) DEFAULT 'army_rule',
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(faction_version_id)
);

-- Detachment options available to a faction at a specific version
CREATE TABLE detachments (
   id SERIAL PRIMARY KEY,
   faction_version_id INTEGER NOT NULL REFERENCES faction_versions(id) ON DELETE CASCADE,
   name VARCHAR(200) NOT NULL,
   is_default BOOLEAN DEFAULT FALSE,
   detachment_rule_name VARCHAR(200), -- 10th edition detachment rule
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ENHANCEMENT TABLES
-- =====================================================

-- Enhancements available within detachments (10th edition structure)
CREATE TABLE enhancements (
   id SERIAL PRIMARY KEY,
   detachment_id INTEGER NOT NULL REFERENCES detachments(id) ON DELETE CASCADE,
   name VARCHAR(200) NOT NULL,
   points_cost INTEGER DEFAULT 0,
   max_per_army INTEGER DEFAULT 1, -- Usually 3 total in 10th
   restrictions TEXT, -- e.g., "Character models only"
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- UNIT TABLES
-- =====================================================

-- Base unit definitions
CREATE TABLE units (
   id SERIAL PRIMARY KEY,
   name VARCHAR(200) NOT NULL UNIQUE,
   unit_type VARCHAR(50), -- 'character', 'battleline', 'vehicle', etc.
   is_active BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unit states at specific versions for specific factions
CREATE TABLE unit_versions (
   id SERIAL PRIMARY KEY,
   unit_id INTEGER NOT NULL REFERENCES units(id) ON DELETE CASCADE,
   faction_version_id INTEGER NOT NULL REFERENCES faction_versions(id) ON DELETE CASCADE,
   base_points_cost INTEGER NOT NULL,
   min_models INTEGER DEFAULT 1,
   max_models INTEGER DEFAULT 1,
   battlefield_role VARCHAR(50), -- 'HQ', 'Troops', 'Elites', etc.
   power_level INTEGER, -- If still tracked
   base_size VARCHAR(50),
   is_legends BOOLEAN DEFAULT FALSE,
   is_epic_hero BOOLEAN DEFAULT FALSE,
   can_be_battleline BOOLEAN DEFAULT FALSE, -- 10th edition conditional battleline
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(unit_id, faction_version_id)
);

-- Which enhancements CAN be applied to which units
CREATE TABLE unit_enhancement_compatibility (
   id SERIAL PRIMARY KEY,
   unit_version_id INTEGER NOT NULL REFERENCES unit_versions(id) ON DELETE CASCADE,
   enhancement_id INTEGER NOT NULL REFERENCES enhancements(id) ON DELETE CASCADE,
   is_valid BOOLEAN DEFAULT TRUE,
   restrictions TEXT, -- Additional restrictions beyond enhancement base restrictions
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(unit_version_id, enhancement_id)
);

-- =====================================================
-- WARGEAR TABLES
-- =====================================================

-- Base wargear definitions
CREATE TABLE wargear (
   id SERIAL PRIMARY KEY,
   name VARCHAR(200) NOT NULL UNIQUE,
   category VARCHAR(50), -- 'melee', 'ranged', 'other'
   is_weapon BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wargear options available to units
CREATE TABLE unit_wargear_options (
   id SERIAL PRIMARY KEY,
   unit_version_id INTEGER NOT NULL REFERENCES unit_versions(id) ON DELETE CASCADE,
   wargear_id INTEGER NOT NULL REFERENCES wargear(id) ON DELETE CASCADE,
   is_default BOOLEAN DEFAULT FALSE, -- Unit comes with this by default
   is_optional BOOLEAN DEFAULT TRUE,  -- Can be removed/replaced
   points_cost INTEGER DEFAULT 0,
   max_per_unit INTEGER, -- How many can be taken
   models_affected INTEGER, -- How many models can take this
   replacement_for INTEGER REFERENCES wargear(id), -- What it replaces if anything
   mutually_exclusive_group VARCHAR(50), -- Items in same group can't be taken together
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(unit_version_id, wargear_id)
);

-- =====================================================
-- SCRAPED DATA TRACKING
-- =====================================================

-- Track what we've scraped from Wahapedia
CREATE TABLE wahapedia_scrape_state (
   id SERIAL PRIMARY KEY,
   entity_type VARCHAR(50) NOT NULL, -- 'faction', 'unit', 'enhancement', 'wargear'
   entity_identifier VARCHAR(200) NOT NULL, -- Wahapedia's identifier/URL slug
   wahapedia_url TEXT,
   content_hash VARCHAR(64), -- SHA256 for change detection
   last_seen_version_snapshot_id INTEGER REFERENCES version_snapshots(id),
   last_scraped_at TIMESTAMP NOT NULL,
   is_active BOOLEAN DEFAULT TRUE, -- False if removed from Wahapedia
   scrape_status VARCHAR(20) DEFAULT 'success', -- 'success', 'failed', 'partial'
   error_message TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(entity_type, entity_identifier)
);

-- Map Wahapedia identifiers to our database entities
CREATE TABLE source_mappings (
   id SERIAL PRIMARY KEY,
   source VARCHAR(50) DEFAULT 'wahapedia',
   source_identifier VARCHAR(200) NOT NULL,
   entity_type VARCHAR(50) NOT NULL, -- 'faction', 'unit', 'enhancement', 'wargear'
   entity_id INTEGER NOT NULL, -- References appropriate table based on entity_type
   confidence_score DECIMAL(3,2) DEFAULT 1.00, -- Confidence in the mapping
   is_verified BOOLEAN DEFAULT FALSE, -- Manually verified
   mapping_metadata JSONB, -- Additional mapping information
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(source, source_identifier, entity_type)
);

-- Track scraping runs
CREATE TABLE scrape_logs (
   id SERIAL PRIMARY KEY,
   source VARCHAR(50) NOT NULL DEFAULT 'wahapedia',
   faction_id INTEGER REFERENCES factions(id),
   version_snapshot_id INTEGER REFERENCES version_snapshots(id),
   scrape_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'faction', 'unit'
   status VARCHAR(20) NOT NULL, -- 'started', 'completed', 'failed'
   started_at TIMESTAMP NOT NULL,
   completed_at TIMESTAMP,
   items_processed INTEGER DEFAULT 0,
   items_failed INTEGER DEFAULT 0,
   error_message TEXT,
   scrape_metadata JSONB -- Additional information about the scrape
);

-- Track changes detected between scrapes
CREATE TABLE change_logs (
   id SERIAL PRIMARY KEY,
   version_snapshot_id INTEGER NOT NULL REFERENCES version_snapshots(id),
   entity_type VARCHAR(50) NOT NULL,
   entity_id INTEGER NOT NULL,
   change_type VARCHAR(20) NOT NULL, -- 'added', 'removed', 'modified'
   field_changed VARCHAR(100),
   old_value TEXT,
   new_value TEXT,
   detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- REDIS MESSAGE QUEUE TRACKING
-- =====================================================

-- Track messages published to Redis
CREATE TABLE redis_messages (
   id SERIAL PRIMARY KEY,
   message_type VARCHAR(50) NOT NULL, -- 'faction_discovered', 'unit_extracted', etc.
   channel VARCHAR(100) NOT NULL,
   payload JSONB NOT NULL,
   status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'published', 'acknowledged', 'failed'
   published_at TIMESTAMP,
   acknowledged_at TIMESTAMP,
   retry_count INTEGER DEFAULT 0,
   error_message TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Version tracking indexes
CREATE INDEX idx_updates_current ON warhammer_updates(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_updates_type ON warhammer_updates(update_type);
CREATE INDEX idx_version_snapshots_current ON version_snapshots(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_version_snapshots_date ON version_snapshots(effective_date DESC);

-- Faction indexes
CREATE INDEX idx_faction_versions_faction ON faction_versions(faction_id);
CREATE INDEX idx_faction_versions_snapshot ON faction_versions(version_snapshot_id);
CREATE INDEX idx_detachments_faction ON detachments(faction_version_id);

-- Unit indexes
CREATE INDEX idx_unit_versions_unit ON unit_versions(unit_id);
CREATE INDEX idx_unit_versions_faction ON unit_versions(faction_version_id);
CREATE INDEX idx_unit_enhancement_unit ON unit_enhancement_compatibility(unit_version_id);
CREATE INDEX idx_unit_enhancement_enhancement ON unit_enhancement_compatibility(enhancement_id);

-- Wargear indexes
CREATE INDEX idx_unit_wargear_unit ON unit_wargear_options(unit_version_id);
CREATE INDEX idx_unit_wargear_wargear ON unit_wargear_options(wargear_id);

-- Enhancement indexes
CREATE INDEX idx_enhancements_detachment ON enhancements(detachment_id);

-- Scraping indexes
CREATE INDEX idx_scrape_state_type ON wahapedia_scrape_state(entity_type);
CREATE INDEX idx_scrape_state_identifier ON wahapedia_scrape_state(entity_identifier);
CREATE INDEX idx_scrape_state_active ON wahapedia_scrape_state(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_source_mappings_lookup ON source_mappings(source, source_identifier, entity_type);
CREATE INDEX idx_scrape_logs_date ON scrape_logs(started_at DESC);
CREATE INDEX idx_change_logs_snapshot ON change_logs(version_snapshot_id);
CREATE INDEX idx_redis_messages_status ON redis_messages(status);
CREATE INDEX idx_redis_messages_created ON redis_messages(created_at DESC);

-- =====================================================
-- HELPER VIEWS
-- =====================================================

-- Current version info
CREATE VIEW current_version AS
SELECT 
   vs.id as version_snapshot_id,
   wmv.version_number as major_version,
   wmv.name as major_version_name,
   wu.version_code as update_code,
   wu.name as update_name,
   wu.update_type,
   vs.effective_date
FROM version_snapshots vs
JOIN warhammer_major_versions wmv ON vs.major_version_id = wmv.id
LEFT JOIN warhammer_updates wu ON vs.update_id = wu.id
WHERE vs.is_current = TRUE;

-- Current factions with their detachments
CREATE VIEW current_factions AS
SELECT 
   f.id as faction_id,
   f.name as faction_name,
   f.code as faction_code,
   fv.has_codex,
   ar.name as army_rule,
   d.name as detachment_name,
   d.is_default as is_default_detachment
FROM faction_versions fv
JOIN factions f ON fv.faction_id = f.id
LEFT JOIN army_rules ar ON ar.faction_version_id = fv.id
LEFT JOIN detachments d ON d.faction_version_id = fv.id
JOIN version_snapshots vs ON fv.version_snapshot_id = vs.id
WHERE vs.is_current = TRUE
   AND fv.is_playable = TRUE
ORDER BY f.name, d.name;

-- Units with their total cost calculation capability
CREATE VIEW current_units_with_costs AS
SELECT 
   f.name as faction_name,
   f.code as faction_code,
   u.name as unit_name,
   uv.base_points_cost,
   uv.min_models,
   uv.max_models,
   uv.battlefield_role,
   uv.is_epic_hero,
   uv.can_be_battleline,
   COUNT(DISTINCT e.id) as available_enhancements,
   COUNT(DISTINCT uwo.wargear_id) as wargear_options
FROM unit_versions uv
JOIN units u ON uv.unit_id = u.id
JOIN faction_versions fv ON uv.faction_version_id = fv.id
JOIN factions f ON fv.faction_id = f.id
LEFT JOIN detachments d ON d.faction_version_id = fv.id
LEFT JOIN enhancements e ON e.detachment_id = d.id
LEFT JOIN unit_enhancement_compatibility uec ON uec.unit_version_id = uv.id AND uec.enhancement_id = e.id
LEFT JOIN unit_wargear_options uwo ON uwo.unit_version_id = uv.id
JOIN version_snapshots vs ON fv.version_snapshot_id = vs.id
WHERE vs.is_current = TRUE
   AND NOT uv.is_legends
GROUP BY f.name, f.code, u.name, uv.base_points_cost, uv.min_models, 
         uv.max_models, uv.battlefield_role, uv.is_epic_hero, uv.can_be_battleline
ORDER BY f.name, u.name;

-- Enhancements by detachment
CREATE VIEW current_enhancements AS
SELECT 
   f.name as faction_name,
   d.name as detachment_name,
   e.name as enhancement_name,
   e.points_cost,
   e.restrictions
FROM enhancements e
JOIN detachments d ON e.detachment_id = d.id
JOIN faction_versions fv ON d.faction_version_id = fv.id
JOIN factions f ON fv.faction_id = f.id
JOIN version_snapshots vs ON fv.version_snapshot_id = vs.id
WHERE vs.is_current = TRUE
ORDER BY f.name, d.name, e.name;

-- Recent scraping activity
CREATE VIEW recent_scraping_activity AS
SELECT 
   sl.scrape_type,
   sl.status,
   sl.started_at,
   sl.completed_at,
   sl.items_processed,
   sl.items_failed,
   f.name as faction_name,
   vs.effective_date as version_date
FROM scrape_logs sl
LEFT JOIN factions f ON sl.faction_id = f.id
LEFT JOIN version_snapshots vs ON sl.version_snapshot_id = vs.id
WHERE sl.started_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
ORDER BY sl.started_at DESC;

-- =====================================================
-- FUNCTIONS AND TRIGGERS
-- =====================================================

-- Update timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Add update triggers to relevant tables
CREATE TRIGGER update_warhammer_major_versions_updated_at 
   BEFORE UPDATE ON warhammer_major_versions 
   FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_warhammer_updates_updated_at 
   BEFORE UPDATE ON warhammer_updates 
   FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_factions_updated_at 
   BEFORE UPDATE ON factions 
   FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_units_updated_at 
   BEFORE UPDATE ON units 
   FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wargear_updated_at 
   BEFORE UPDATE ON wargear 
   FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wahapedia_scrape_state_updated_at 
   BEFORE UPDATE ON wahapedia_scrape_state 
   FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_source_mappings_updated_at 
   BEFORE UPDATE ON source_mappings 
   FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to ensure only one current version snapshot
CREATE OR REPLACE FUNCTION ensure_single_current_version()
RETURNS TRIGGER AS $$
BEGIN
   IF NEW.is_current = TRUE THEN
      UPDATE version_snapshots 
      SET is_current = FALSE 
      WHERE is_current = TRUE 
         AND id != NEW.id;
   END IF;
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER ensure_single_current_version_trigger
   BEFORE INSERT OR UPDATE ON version_snapshots
   FOR EACH ROW EXECUTE FUNCTION ensure_single_current_version();

-- Function to ensure only one current update per type
CREATE OR REPLACE FUNCTION ensure_single_current_update()
RETURNS TRIGGER AS $$
BEGIN
   IF NEW.is_current = TRUE THEN
      UPDATE warhammer_updates 
      SET is_current = FALSE 
      WHERE is_current = TRUE 
         AND major_version_id = NEW.major_version_id
         AND update_type = NEW.update_type
         AND id != NEW.id;
   END IF;
   RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER ensure_single_current_update_trigger
   BEFORE INSERT OR UPDATE ON warhammer_updates
   FOR EACH ROW EXECUTE FUNCTION ensure_single_current_update();

-- =====================================================
-- INITIAL DATA INSERTION
-- =====================================================

-- Insert 10th Edition as the current major version
INSERT INTO warhammer_major_versions (version_number, name, release_date, is_current)
VALUES ('10th', '10th Edition', '2023-06-10', TRUE);

-- Insert initial version snapshot for 10th edition launch
INSERT INTO version_snapshots (major_version_id, update_id, effective_date, is_current)
VALUES (
   (SELECT id FROM warhammer_major_versions WHERE version_number = '10th'),
   NULL,
   '2023-06-10',
   FALSE -- Will be updated when we add current dataslate
);

-- =====================================================
-- PERMISSIONS (adjust as needed)
-- =====================================================

-- Grant permissions to application user (replace 'app_user' with your actual user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;
