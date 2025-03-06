#!/usr/bin/env python
"""
Script to migrate existing food preferences from profiles.food_preferences JSON
to the new normalized tables.
"""
import asyncio
import json
import logging
from typing import Dict, Any, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import async_session
from domains.profiles.models import Profile, UserFoodPreference, UserPreferenceSettings

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def migrate_user_preferences(session: AsyncSession, user_id: int, 
                                  food_prefs: Dict[str, Any]) -> None:
    """Migrate a single user's food preferences to the new tables."""
    logger.info(f"Migrating preferences for user {user_id}")
    
    # Extract preferences
    dietary_restrictions = food_prefs.get('dietary_restrictions', [])
    allergies = food_prefs.get('allergies', [])
    preferred_cuisines = food_prefs.get('preferred_cuisines', [])
    spice_level = food_prefs.get('spice_level')
    
    # Migrate array-type preferences
    for restriction in dietary_restrictions:
        session.add(UserFoodPreference(
            user_id=user_id,
            preference_type='dietary_restrictions',
            preference_value=restriction
        ))
    
    for allergy in allergies:
        session.add(UserFoodPreference(
            user_id=user_id,
            preference_type='allergies',
            preference_value=allergy
        ))
    
    for cuisine in preferred_cuisines:
        session.add(UserFoodPreference(
            user_id=user_id,
            preference_type='preferred_cuisines',
            preference_value=cuisine
        ))
    
    # Migrate scalar preferences
    # First check if user already has preference settings
    result = await session.execute(
        select(UserPreferenceSettings).where(UserPreferenceSettings.user_id == user_id)
    )
    settings = result.scalars().first()
    
    if settings:
        # Update existing settings
        if spice_level:
            settings.spice_level = spice_level
    else:
        # Create new settings
        session.add(UserPreferenceSettings(
            user_id=user_id,
            spice_level=spice_level,
            additional_info=None  # We don't have this in the JSON structure
        ))
    
    # Commit changes
    await session.commit()
    logger.info(f"Successfully migrated preferences for user {user_id}")

async def migrate_all_preferences() -> None:
    """Migrate all users' food preferences from the JSON column to the new tables."""
    logger.info("Starting migration of food preferences")
    
    async with async_session() as session:
        # Get all profiles with food preferences
        result = await session.execute(
            select(Profile).where(Profile.food_preferences.is_not(None))
        )
        profiles = result.scalars().all()
        
        logger.info(f"Found {len(profiles)} profiles with food preferences")
        
        # Migrate each profile's preferences
        for profile in profiles:
            if profile.food_preferences:
                try:
                    await migrate_user_preferences(session, profile.id, profile.food_preferences)
                except Exception as e:
                    logger.error(f"Error migrating preferences for user {profile.id}: {e}")
    
    logger.info("Migration completed")

if __name__ == "__main__":
    asyncio.run(migrate_all_preferences()) 