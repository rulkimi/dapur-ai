# Recipe Matching SQL Queries

This document provides example SQL queries for matching recipes with user food preferences based on the new normalized database structure.

## Database Structure

We have the following tables for food preferences:

- `user_food_preferences`: Stores array-type preferences (dietary restrictions, allergies, cuisines)
- `user_preference_settings`: Stores scalar preferences (spice level, additional info)

## Example Queries

### 1. Find Recipes Matching Dietary Restrictions

This query finds recipes that are compatible with a user's dietary restrictions:

```sql
-- Find recipes that match dietary restrictions
SELECT r.* 
FROM recipes r
WHERE NOT EXISTS (
    -- Check if any required dietary restriction is not compatible with this recipe
    SELECT 1 
    FROM user_food_preferences ufp
    WHERE ufp.user_id = :user_id 
      AND ufp.preference_type = 'dietary_restrictions'
      AND NOT EXISTS (
          -- Check if this dietary restriction is compatible with this recipe
          SELECT 1 
          FROM recipe_dietary_restrictions rdr
          WHERE rdr.recipe_id = r.id
            AND rdr.restriction = ufp.preference_value
      )
);
```

### 2. Find Recipes Without Allergenic Ingredients

Find recipes that don't contain ingredients the user is allergic to:

```sql
-- Find recipes without allergenic ingredients
SELECT r.* 
FROM recipes r
WHERE NOT EXISTS (
    -- Check if any ingredient matches user allergies
    SELECT 1 
    FROM recipe_ingredients ri
    JOIN ingredients i ON ri.ingredient_id = i.id
    JOIN user_food_preferences ufp ON (
        ufp.user_id = :user_id 
        AND ufp.preference_type = 'allergies'
        AND (
            -- Match exact ingredient names
            i.name = ufp.preference_value
            -- Or ingredient contains the allergic term
            OR i.name LIKE CONCAT('%', ufp.preference_value, '%')
        )
    )
    WHERE ri.recipe_id = r.id
);
```

### 3. Find Recipes with Preferred Cuisines

Find recipes that match a user's preferred cuisines:

```sql
-- Find recipes with preferred cuisines
SELECT r.* 
FROM recipes r
WHERE EXISTS (
    -- Match recipe cuisine with user's preferred cuisines
    SELECT 1 
    FROM user_food_preferences ufp
    WHERE ufp.user_id = :user_id 
      AND ufp.preference_type = 'preferred_cuisines'
      AND r.cuisine = ufp.preference_value
);
```

### 4. Filter by Spice Level

Filter recipes based on the user's spice level preference:

```sql
-- Filter recipes by spice level
SELECT r.* 
FROM recipes r
INNER JOIN user_preference_settings ups ON ups.user_id = :user_id
WHERE 
    -- Map spice level values to numeric scale
    (CASE 
        WHEN r.spice_level = 'Mild' THEN 1
        WHEN r.spice_level = 'Medium' THEN 2
        WHEN r.spice_level = 'Strong' THEN 3
        ELSE 2 -- default
    END)
    <= 
    (CASE 
        WHEN ups.spice_level = 'Mild' THEN 1
        WHEN ups.spice_level = 'Medium' THEN 2
        WHEN ups.spice_level = 'Strong' THEN 3
        ELSE 3 -- If not specified, default to showing all
    END);
```

### 5. Combined Query for Recipe Recommendations

A comprehensive query that combines all preferences to recommend recipes:

```sql
-- Combined recipe recommendation query
SELECT 
    r.*,
    -- Relevance score based on multiple factors
    (
        -- Score for matching cuisine (6 points)
        (CASE WHEN EXISTS (
            SELECT 1 FROM user_food_preferences ufp
            WHERE ufp.user_id = :user_id 
              AND ufp.preference_type = 'preferred_cuisines'
              AND r.cuisine = ufp.preference_value
        ) THEN 6 ELSE 0 END) +
        
        -- Score for matching spice level - closer match gets higher score (max 3 points)
        (3 - ABS(
            (CASE 
                WHEN r.spice_level = 'Mild' THEN 1
                WHEN r.spice_level = 'Medium' THEN 2
                WHEN r.spice_level = 'Strong' THEN 3
                ELSE 2
            END) - 
            (SELECT CASE 
                WHEN ups.spice_level = 'Mild' THEN 1
                WHEN ups.spice_level = 'Medium' THEN 2
                WHEN ups.spice_level = 'Strong' THEN 3
                ELSE 2
            END
            FROM user_preference_settings ups 
            WHERE ups.user_id = :user_id)
        ))
    ) AS relevance_score
FROM recipes r
WHERE 
    -- Must not violate dietary restrictions
    NOT EXISTS (
        SELECT 1 
        FROM user_food_preferences ufp
        WHERE ufp.user_id = :user_id 
          AND ufp.preference_type = 'dietary_restrictions'
          AND NOT EXISTS (
              SELECT 1 
              FROM recipe_dietary_restrictions rdr
              WHERE rdr.recipe_id = r.id
                AND rdr.restriction = ufp.preference_value
          )
    )
    -- Must not contain allergenic ingredients
    AND NOT EXISTS (
        SELECT 1 
        FROM recipe_ingredients ri
        JOIN ingredients i ON ri.ingredient_id = i.id
        JOIN user_food_preferences ufp ON (
            ufp.user_id = :user_id 
            AND ufp.preference_type = 'allergies'
            AND (
                i.name = ufp.preference_value
                OR i.name LIKE CONCAT('%', ufp.preference_value, '%')
            )
        )
        WHERE ri.recipe_id = r.id
    )
ORDER BY relevance_score DESC, r.rating DESC
LIMIT 10;
```

## Implementation Notes

1. These queries assume the existence of recipe-related tables like `recipes`, `recipe_ingredients`, `ingredients`, and `recipe_dietary_restrictions`.
2. The actual table structure for recipes may vary and these queries should be adapted accordingly.
3. For performance, appropriate indexes should be created on all join and filter columns.
4. Consider using a full-text search engine like Elasticsearch for more sophisticated matching of preferences, especially for allergies and ingredients. 