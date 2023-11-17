export const curry = (fn: Function) =>
    function c(...args: any[]): any {
        return args.length >= fn.length
            ? fn(...args)
            : c.bind(null, ...args)
    }

export function log(...data: any[]) {
    if (import.meta.env.DEV) {
        console.log(...data)
    }
}

export function unique(iterable: any[]) {
    return [...new Set(iterable)]
}

export function isBlobUrl(url: string) {
    return url.startsWith('blob:')
}
