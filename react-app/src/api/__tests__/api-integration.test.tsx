/**
 * API Integration Test Examples
 *
 * These tests demonstrate how to use the API client layer.
 * Run with: npm run test (when test setup is complete)
 */

import { describe, it, expect } from 'vitest';
import { samplesApi, kitsApi, preferencesApi } from '@/api';

describe('API Client Integration', () => {
  describe('Samples API', () => {
    it('should list samples', async () => {
      const response = await samplesApi.list({ page: 1, limit: 10 });
      expect(response).toHaveProperty('items');
      expect(response).toHaveProperty('total');
      expect(Array.isArray(response.items)).toBe(true);
    });

    it('should filter samples by genre', async () => {
      const response = await samplesApi.list({ genre: 'hip-hop' });
      expect(response.items.every(s => s.genre === 'hip-hop')).toBe(true);
    });

    it('should filter samples by BPM range', async () => {
      const response = await samplesApi.list({ bpm_min: 80, bpm_max: 120 });
      expect(response.items.every(s =>
        s.bpm && s.bpm >= 80 && s.bpm <= 120
      )).toBe(true);
    });
  });

  describe('Kits API', () => {
    it('should create a new kit', async () => {
      const kit = await kitsApi.create({
        name: 'Test Kit',
        description: 'A test kit',
      });
      expect(kit).toHaveProperty('id');
      expect(kit.name).toBe('Test Kit');
    });

    it('should assign sample to pad', async () => {
      // First create a kit
      const kit = await kitsApi.create({ name: 'Test Kit' });

      // Then assign a sample
      const assignment = await kitsApi.assignSample(kit.id, {
        sample_id: 1,
        pad_bank: 'A',
        pad_number: 1,
      });

      expect(assignment.kit_id).toBe(kit.id);
      expect(assignment.pad_bank).toBe('A');
      expect(assignment.pad_number).toBe(1);
    });

    it('should build kit with AI', async () => {
      const kit = await kitsApi.buildWithAI('Create a lo-fi hip-hop kit');
      expect(kit).toHaveProperty('id');
      expect(kit.samples.length).toBeGreaterThan(0);
    });
  });

  describe('Preferences API', () => {
    it('should get user preferences', async () => {
      const prefs = await preferencesApi.get();
      expect(prefs).toHaveProperty('ai_model');
      expect(prefs).toHaveProperty('auto_analysis');
      expect(prefs).toHaveProperty('theme');
    });

    it('should update preferences', async () => {
      const updated = await preferencesApi.update({
        ai_model: 'qwen3-235b',
        auto_analysis: true,
      });
      expect(updated.ai_model).toBe('qwen3-235b');
      expect(updated.auto_analysis).toBe(true);
    });
  });
});
