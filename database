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
   major_version_id INTEGER NOT NULL REFERENCES warhammer_major_versions(id),
   update_type VARCHAR(50) NOT NULL, -- 'errata', 'dataslate', 'faq', 'munitorum_field_manual'
   version_code VARCHAR(50) NOT NULL,
   name VARCHAR(200) NOT NULL,
   release_date DATE NOT NULL,
   is_current BOOLEAN DEFAULT FALSE,
   change_summary TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(major_version_id, version_code)
);

-- Combined version snapshot for tracking unit/faction states
CREATE TABLE version_snapshots (
   id SERIAL PRIMARY KEY,
   major_version_id INTEGER NOT NULL REFERENCES warhammer_major_versions(id),
   update_id INTEGER REFERENCES warhammer_updates(id),
   effective_date DATE NOT NULL,
   is_current BOOLEAN DEFAULT FALSE,
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
   is_active BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Faction states at specific versions
CREATE TABLE faction_versions (
   id SERIAL PRIMARY KEY,
   faction_id INTEGER NOT NULL REFERENCES factions(id),
   version_snapshot_id INTEGER NOT NULL REFERENCES version_snapshots(id),
   army_rule_name VARCHAR(200), -- Single army rule name per faction
   is_playable BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(faction_id, version_snapshot_id)
);

-- Detachment options available to a faction at a specific version
CREATE TABLE detachments (
   id SERIAL PRIMARY KEY,
   faction_version_id INTEGER NOT NULL REFERENCES faction_versions(id),
   name VARCHAR(200) NOT NULL,
   is_default BOOLEAN DEFAULT FALSE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ENHANCEMENT TABLES
-- =====================================================

-- Enhancements available within detachments at specific versions
CREATE TABLE enhancements (
   id SERIAL PRIMARY KEY,
   detachment_id INTEGER NOT NULL REFERENCES detachments(id),
   name VARCHAR(200) NOT NULL,
   points_cost INTEGER DEFAULT 0, -- Cost to add this enhancement to a unit
   max_per_army INTEGER DEFAULT 1,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- UNIT TABLES
-- =====================================================

-- Base unit definitions
CREATE TABLE units (
   id SERIAL PRIMARY KEY,
   name VARCHAR(200) NOT NULL UNIQUE,
   is_active BOOLEAN DEFAULT TRUE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Unit states at specific versions for specific factions
CREATE TABLE unit_versions (
   id SERIAL PRIMARY KEY,
   unit_id INTEGER NOT NULL REFERENCES units(id),
   faction_version_id INTEGER NOT NULL REFERENCES faction_versions(id),
   enhancement_id INTEGER REFERENCES enhancements(id), -- NULL if no enhancement
   base_points_cost INTEGER NOT NULL, -- Base cost of the unit without wargear or enhancements
   battlefield_role VARCHAR(50), -- HQ, Troops, Elites, etc.
   base_size VARCHAR(50),
   is_legends BOOLEAN DEFAULT FALSE,
   is_epic_hero BOOLEAN DEFAULT FALSE,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(unit_id, faction_version_id, enhancement_id)
);

-- =====================================================
-- WARGEAR TABLES
-- =====================================================

-- Base wargear definitions
CREATE TABLE wargear (
   id SERIAL PRIMARY KEY,
   name VARCHAR(200) NOT NULL UNIQUE,
   category VARCHAR(50), -- Melee, Ranged, Other
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wargear options available to units
CREATE TABLE unit_wargear_options (
   id SERIAL PRIMARY KEY,
   unit_version_id INTEGER NOT NULL REFERENCES unit_versions(id),
   wargear_id INTEGER NOT NULL REFERENCES wargear(id),
   is_default BOOLEAN DEFAULT FALSE, -- TRUE if unit comes with this by default
   is_optional BOOLEAN DEFAULT TRUE,  -- FALSE if cannot be removed
   max_per_unit INTEGER,
   points_cost INTEGER DEFAULT 0,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
   UNIQUE(unit_version_id, wargear_id)
);

-- =====================================================
-- SCRAPED DATA TRACKING
-- =====================================================

-- Track what we've scraped and when
CREATE TABLE scrape_logs (
   id SERIAL PRIMARY KEY,
   source VARCHAR(50) NOT NULL, -- 'wahapedia', 'gw_site', etc.
   faction_id INTEGER REFERENCES factions(id),
   version_snapshot_id INTEGER REFERENCES version_snapshots(id),
   scrape_type VARCHAR(50) NOT NULL, -- 'full', 'incremental', 'faction', 'unit'
   status VARCHAR(20) NOT NULL, -- 'started', 'completed', 'failed'
   started_at TIMESTAMP NOT NULL,
   completed_at TIMESTAMP,
   items_processed INTEGER DEFAULT 0,
   items_failed INTEGER DEFAULT 0,
   error_message TEXT
);

-- Track changes detected between scrapes
CREATE TABLE change_logs (
   id SERIAL PRIMARY KEY,
   version_snapshot_id INTEGER NOT NULL REFERENCES version_snapshots(id),
   entity_type VARCHAR(50) NOT NULL, -- 'faction', 'unit', 'wargear', 'enhancement'
   entity_id INTEGER NOT NULL,
   change_type VARCHAR(20) NOT NULL, -- 'added', 'removed', 'modified'
   field_changed VARCHAR(100),
   old_value TEXT,
   new_value TEXT,
   detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_faction_versions_faction ON faction_versions(faction_id);
CREATE INDEX idx_faction_versions_snapshot ON faction_versions(version_snapshot_id);
CREATE INDEX idx_unit_versions_unit ON unit_versions(unit_id);
CREATE INDEX idx_unit_versions_faction ON unit_versions(faction_version_id);
CREATE INDEX idx_unit_versions_enhancement ON unit_versions(enhancement_id);
CREATE INDEX idx_unit_wargear_unit ON unit_wargear_options(unit_version_id);
CREATE INDEX idx_enhancements_detachment ON enhancements(detachment_id);
CREATE INDEX idx_scrape_logs_date ON scrape_logs(started_at DESC);
CREATE INDEX idx_change_logs_snapshot ON change_logs(version_snapshot_id);
CREATE INDEX idx_version_snapshots_current ON version_snapshots(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_updates_current ON warhammer_updates(is_current) WHERE is_current = TRUE;
CREATE INDEX idx_updates_type ON warhammer_updates(update_type);

-- =====================================================
-- HELPER VIEWS
-- =====================================================

-- Current version info
CREATE VIEW current_version AS
SELECT 
   vs.id as version_snapshot_id,
   wmv.version_number as major_version,
   wu.version_code as update_code,
   wu.name as update_name,
   wu.update_type,
   vs.effective_date
FROM version_snapshots vs
JOIN warhammer_major_versions wmv ON vs.major_version_id = wmv.id
LEFT JOIN warhammer_updates wu ON vs.update_id = wu.id
WHERE vs.is_current = TRUE;

-- Units with their total cost (base + enhancement)
CREATE VIEW current_units_total_cost AS
SELECT 
   f.name as faction_name,
   u.name as unit_name,
   e.name as enhancement_name,
   uv.base_points_cost,
   COALESCE(e.points_cost, 0) as enhancement_cost,
   (uv.base_points_cost + COALESCE(e.points_cost, 0)) as total_unit_cost
FROM unit_versions uv
JOIN units u ON uv.unit_id = u.id
JOIN faction_versions fv ON uv.faction_version_id = fv.id
JOIN factions f ON fv.faction_id = f.id
LEFT JOIN enhancements e ON uv.enhancement_id = e.id
JOIN version_snapshots vs ON fv.version_snapshot_id = vs.id
WHERE vs.is_current = TRUE
   AND NOT uv.is_legends
ORDER BY f.name, u.name;

-- Units with their available wargear and full cost calculation
CREATE VIEW current_units_full_loadout AS
SELECT 
   f.name as faction_name,
   u.name as unit_name,
   e.name as enhancement_name,
   w.name as wargear_name,
   uv.base_points_cost,
   COALESCE(e.points_cost, 0) as enhancement_cost,
   uwo.points_cost as wargear_cost,
   uwo.is_default,
   uwo.is_optional
FROM unit_versions uv
JOIN units u ON uv.unit_id = u.id
JOIN faction_versions fv ON uv.faction_version_id = fv.id
JOIN factions f ON fv.faction_id = f.id
LEFT JOIN enhancements e ON uv.enhancement_id = e.id
LEFT JOIN unit_wargear_options uwo ON uwo.unit_version_id = uv.id
LEFT JOIN wargear w ON uwo.wargear_id = w.id
JOIN version_snapshots vs ON fv.version_snapshot_id = vs.id
WHERE vs.is_current = TRUE
   AND NOT uv.is_legends
ORDER BY f.name, u.name, w.name;

-- Current factions with their detachments and enhancements
CREATE VIEW current_faction_detachments AS
SELECT 
   f.name as faction_name,
   fv.army_rule_name,
   d.name as detachment_name,
   e.name as enhancement_name,
   e.points_cost as enhancement_cost
FROM faction_versions fv
JOIN factions f ON fv.faction_id = f.id
JOIN detachments d ON d.faction_version_id = fv.id
LEFT JOIN enhancements e ON e.detachment_id = d.id
JOIN version_snapshots vs ON fv.version_snapshot_id = vs.id
WHERE vs.is_current = TRUE
   AND fv.is_playable = TRUE
ORDER BY f.name, d.name, e.name;
