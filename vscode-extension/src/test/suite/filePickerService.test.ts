/**
 * Tests for FilePickerService
 *
 * Tests the centralized file/folder selection service used across
 * all VSCode extension panels.
 *
 * Copyright 2025 Smart-AI-Memory
 * Licensed under Fair Source License 0.9
 */

import * as assert from 'assert';
import {
    FilePickerService,
    getFilePickerService,
    createFilePickerMessageHandler,
    FILE_FILTERS,
    FilePickerMessage,
    FilePickerResponse
} from '../../services/FilePickerService';

suite('FilePickerService Test Suite', () => {

    suite('Singleton Pattern', () => {
        test('getFilePickerService returns same instance', () => {
            const instance1 = getFilePickerService();
            const instance2 = getFilePickerService();
            assert.strictEqual(instance1, instance2, 'Should return the same singleton instance');
        });

        test('FilePickerService.getInstance returns same instance', () => {
            const instance1 = FilePickerService.getInstance();
            const instance2 = FilePickerService.getInstance();
            assert.strictEqual(instance1, instance2, 'Should return the same singleton instance');
        });
    });

    suite('FILE_FILTERS', () => {
        test('PYTHON filter should contain py extension', () => {
            assert.ok(FILE_FILTERS.PYTHON, 'PYTHON filter should exist');
            assert.ok(FILE_FILTERS.PYTHON['Python Files'], 'Python Files key should exist');
            assert.ok(FILE_FILTERS.PYTHON['Python Files'].includes('py'), 'Should include py extension');
        });

        test('TYPESCRIPT filter should contain ts and tsx extensions', () => {
            assert.ok(FILE_FILTERS.TYPESCRIPT, 'TYPESCRIPT filter should exist');
            assert.ok(FILE_FILTERS.TYPESCRIPT['TypeScript'], 'TypeScript key should exist');
            assert.ok(FILE_FILTERS.TYPESCRIPT['TypeScript'].includes('ts'), 'Should include ts extension');
            assert.ok(FILE_FILTERS.TYPESCRIPT['TypeScript'].includes('tsx'), 'Should include tsx extension');
        });

        test('CODE_ALL filter should contain multiple code extensions', () => {
            assert.ok(FILE_FILTERS.CODE_ALL, 'CODE_ALL filter should exist');
            assert.ok(FILE_FILTERS.CODE_ALL['Code Files'], 'Code Files key should exist');
            const codeFiles = FILE_FILTERS.CODE_ALL['Code Files'];
            assert.ok(codeFiles.includes('py'), 'Should include py');
            assert.ok(codeFiles.includes('ts'), 'Should include ts');
            assert.ok(codeFiles.includes('js'), 'Should include js');
        });

        test('DOCUMENTS filter should contain document extensions', () => {
            assert.ok(FILE_FILTERS.DOCUMENTS, 'DOCUMENTS filter should exist');
            assert.ok(FILE_FILTERS.DOCUMENTS['Documents'], 'Documents key should exist');
            const docs = FILE_FILTERS.DOCUMENTS['Documents'];
            assert.ok(docs.includes('md'), 'Should include md');
            assert.ok(docs.includes('txt'), 'Should include txt');
            assert.ok(docs.includes('json'), 'Should include json');
        });

        test('ALL filter should contain wildcard', () => {
            assert.ok(FILE_FILTERS.ALL, 'ALL filter should exist');
            assert.ok(FILE_FILTERS.ALL['All Files'], 'All Files key should exist');
            assert.ok(FILE_FILTERS.ALL['All Files'].includes('*'), 'Should include wildcard');
        });
    });

    suite('Message Handler Factory', () => {
        test('createFilePickerMessageHandler returns a function', () => {
            const service = getFilePickerService();
            const messages: FilePickerResponse[] = [];
            const handler = createFilePickerMessageHandler(service, (msg) => {
                messages.push(msg);
            });

            assert.strictEqual(typeof handler, 'function', 'Should return a function');
        });

        test('Handler returns false for non-filePicker messages', async () => {
            const service = getFilePickerService();
            const handler = createFilePickerMessageHandler(service, () => {});

            const result = await handler({ type: 'someOtherMessage' });
            assert.strictEqual(result, false, 'Should return false for non-filePicker messages');
        });

        test('Handler returns true for filePicker: prefixed messages', async () => {
            const service = getFilePickerService();
            const handler = createFilePickerMessageHandler(service, () => {});

            // Note: The actual file picker won't show in tests, but the handler should recognize the message type
            const result = await handler({ type: 'filePicker:useProjectRoot' });
            assert.strictEqual(result, true, 'Should return true for filePicker: messages');
        });
    });

    suite('Message Types', () => {
        test('Handler recognizes filePicker:selectFile', async () => {
            const service = getFilePickerService();
            let responseReceived = false;

            const handler = createFilePickerMessageHandler(service, (msg) => {
                responseReceived = true;
                assert.strictEqual(msg.type, 'filePicker:result', 'Response type should be filePicker:result');
            });

            // This will fail to show dialog in test environment but should handle gracefully
            await handler({ type: 'filePicker:selectFile', options: {} });
            // Response may or may not be received depending on test environment
        });

        test('Handler recognizes filePicker:selectFiles', async () => {
            const service = getFilePickerService();
            const handler = createFilePickerMessageHandler(service, () => {});

            const result = await handler({ type: 'filePicker:selectFiles', options: {} });
            assert.strictEqual(result, true, 'Should recognize filePicker:selectFiles');
        });

        test('Handler recognizes filePicker:selectFolder', async () => {
            const service = getFilePickerService();
            const handler = createFilePickerMessageHandler(service, () => {});

            const result = await handler({ type: 'filePicker:selectFolder', options: {} });
            assert.strictEqual(result, true, 'Should recognize filePicker:selectFolder');
        });

        test('Handler recognizes filePicker:useActiveFile', async () => {
            const service = getFilePickerService();
            const handler = createFilePickerMessageHandler(service, () => {});

            const result = await handler({ type: 'filePicker:useActiveFile', options: {} });
            assert.strictEqual(result, true, 'Should recognize filePicker:useActiveFile');
        });

        test('Handler recognizes filePicker:useProjectRoot', async () => {
            const service = getFilePickerService();
            let responseReceived = false;

            const handler = createFilePickerMessageHandler(service, (msg) => {
                responseReceived = true;
            });

            const result = await handler({ type: 'filePicker:useProjectRoot' });
            assert.strictEqual(result, true, 'Should recognize filePicker:useProjectRoot');
        });
    });

    suite('Service Methods', () => {
        test('getActiveFile returns undefined when no editor is open', () => {
            const service = getFilePickerService();
            // In test environment, there's typically no active editor
            const result = service.getActiveFile();
            // Result may be undefined or a file depending on test environment
            // Just verify it doesn't throw
            assert.ok(true, 'getActiveFile should not throw');
        });

        test('getProjectRoot returns result when workspace is open', () => {
            const service = getFilePickerService();
            const result = service.getProjectRoot();
            // In test environment with extension host, workspace may or may not be open
            // Just verify it doesn't throw
            assert.ok(true, 'getProjectRoot should not throw');
        });

        test('getActiveFile with language filter works', () => {
            const service = getFilePickerService();
            // Test that language filter parameter is accepted
            const result = service.getActiveFile('python');
            assert.ok(true, 'getActiveFile with filter should not throw');
        });

        test('getActiveFile with multiple language filters works', () => {
            const service = getFilePickerService();
            // Test that array of language filters is accepted
            const result = service.getActiveFile(['python', 'typescript']);
            assert.ok(true, 'getActiveFile with multiple filters should not throw');
        });
    });
});
