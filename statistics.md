
# Music Recommendation System Metrics & Statistics

## Overview

Our Music Recommendation System tracks and analyzes user interactions to provide valuable insights into user behavior and system performance. The collected metrics are stored in dedicated RDS tables (`events_definitions`, `user_events`), capturing a range of user operations within the web application.

## Collected Metrics

The following metrics are tracked:

- **user_signed_up**: When a user signs up
- **user_logged_in**: When a user logs in
- **user_added_track**: When a user adds a track
- **user_liked_recommended_track**: When a user likes a recommended track
- **user_disliked_recommended_track**: When a user dislikes a recommended track
- **user_requested_recommendations**: When a user requests new recommendations
- **user_ignored_recommendations**: When a user ignores the recommendations

## Database Structure

### events_definitions Table

This table maps each event ID to its corresponding event name.

**Example from the RDS:**
![events_mapping_table](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/32aa7a2a-1cbd-4150-a6eb-e9fc920c8875)

### user_events Table
![events_table](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/ed3ab617-2979-4152-b010-c08f7039a6a2)

This table logs all user events, capturing every interaction triggered by users.

**Example from the RDS:**

## Metrics Displayed

### 1. User Event Counts

Displays the total count of each operation that has occurred in the web application across all users.

### 2. Most Liked Tracks

Highlights the tracks that have received the most likes from users.

Pic for metrics 1&2:
![stats1](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/0597ad81-ad29-4451-a023-bd2ec81cac91)

### 3. Average User Operations (Daily Basis)

Analyzes the average number of operations performed by users on a daily basis, providing insights into:

- Average likes vs. dislikes
- Average refresh recommendations vs. ignored recommendations
- Ratio of new users vs. recurring users

![stats2](https://github.com/doritlya1997/music-recommendation-system/assets/64167336/52ddd92b-75c6-4be4-a5d0-b3d649441745)