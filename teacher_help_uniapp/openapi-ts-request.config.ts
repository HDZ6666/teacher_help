import type { GenerateServiceProps } from 'openapi-ts-request'

export default [
  {
    schemaPath: 'http://127.0.0.1:9099/openapi.json',
    serversPath: './src/generated-service',
    requestLibPath: `import request from '@/http/vue-query';\n import { CustomRequestOptions } from '@/http/types';`,
    requestOptionsType: 'CustomRequestOptions',
    isGenReactQuery: true,
    reactQueryMode: 'vue',
    isGenJavaScript: false,
  },
] as GenerateServiceProps[]
