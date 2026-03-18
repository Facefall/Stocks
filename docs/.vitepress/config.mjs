import { defineConfig } from 'vitepress'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 自动生成侧边栏
function generateSidebar() {
  const summariesDir = path.join(__dirname, '../summaries')

  if (!fs.existsSync(summariesDir)) {
    return []
  }

  const files = fs.readdirSync(summariesDir)
    .filter(f => f.endsWith('.md'))
    .sort()
    .reverse()
    .slice(0, 50) // 只显示最近50个

  return [
    {
      text: '历史总结',
      items: files.map(f => {
        const name = f.replace('.md', '')
        return {
          text: name,
          link: `/summaries/${name}`
        }
      })
    }
  ]
}

export default defineConfig({
  title: '财经社区聊天记录',
  description: '群组消息实时总结，让高价值信息不再被刷屏淹没',

  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '搜索', link: '/search' },
      { text: '历史总结', link: '/summaries/' }
    ],

    sidebar: {
      '/summaries/': generateSidebar()
    },

    search: {
      provider: 'local',
      options: {
        detailedView: true
      }
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/andychenggg/Stocks' }
    ],

    footer: {
      message: '基于开源项目构建',
      copyright: 'Copyright © 2025'
    }
  },

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#3eaf7c' }],
    ['meta', { name: 'apple-mobile-web-app-capable', content: 'yes' }],
    ['meta', { name: 'apple-mobile-web-app-status-bar-style', content: 'black' }]
  ],

  markdown: {
    lineNumbers: true
  },

  vite: {
    optimizeDeps: {
      include: ['vue']
    }
  }
})
