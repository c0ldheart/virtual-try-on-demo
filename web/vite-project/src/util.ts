export const curry = (fn: Function) =>
    function c(...args: any[]): any {
        return args.length >= fn.length
            ? fn(...args)
            : c.bind(null, ...args)
    }
