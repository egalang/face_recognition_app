package com.obbsco.sisattendance.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "sis_session")

class SessionManager(private val context: Context) {
    private val accessTokenKey = stringPreferencesKey("access_token")

    suspend fun saveAccessToken(token: String) {
        context.dataStore.edit { prefs ->
            prefs[accessTokenKey] = token
        }
    }

    suspend fun getAccessToken(): String? {
        return context.dataStore.data.map { it[accessTokenKey] }.first()
    }

    suspend fun clear() {
        context.dataStore.edit { it.clear() }
    }
}
